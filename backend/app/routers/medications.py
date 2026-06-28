from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.database import get_db
from app.models import Medication, MedicationLog, ReminderStatus, User
from app.routers.helpers import get_manageable_medication, get_owned_medication
from app.schemas import CameraMedicationCreate, MedicationCreate, MedicationHistoryResponse, MedicationOut, MedicationUpdate
from app.services.audit import log_audit

router = APIRouter(prefix="/medications", tags=["medications"])


def first_text_line(*values: str | None) -> str | None:
    for value in values:
        if not value:
            continue
        for line in value.replace("_", " ").replace("-", " ").splitlines():
            cleaned = line.strip()
            if cleaned:
                return cleaned
    return None


def medication_from_parts(
    *,
    user_id: str,
    name: str | None,
    active_ingredient: str | None,
    dosage: str | None,
    form: str,
    frequency: str | None,
    medication_category: str | None,
    is_prescription: bool,
    notes: str | None,
) -> Medication:
    resolved_name = name or "Unknown medication"
    return Medication(
        user_id=user_id,
        name=resolved_name,
        active_ingredient=active_ingredient or resolved_name,
        dosage=dosage or "confirm with label",
        form=form,
        frequency=frequency or "as directed",
        medication_category=medication_category,
        is_prescription=is_prescription,
        notes=notes,
    )


@router.post("", response_model=MedicationOut, status_code=status.HTTP_201_CREATED)
def create_medication(
    payload: MedicationCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> Medication:
    data = payload.model_dump()
    data["active_ingredient"] = data["active_ingredient"] or data["name"]
    medication = Medication(user_id=current_user.id, **data)
    db.add(medication)
    db.flush()
    log_audit(db, current_user, "create_medication", "medication", medication.id)
    db.commit()
    db.refresh(medication)
    return medication


@router.post("/upload", response_model=MedicationOut, status_code=status.HTTP_201_CREATED)
async def create_medication_from_upload(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
    file: UploadFile = File(...),
    name: str | None = Form(default=None),
    active_ingredient: str | None = Form(default=None),
    activeIngredient: str | None = Form(default=None),
    dosage: str | None = Form(default=None),
    form: str = Form(default="other"),
    frequency: str | None = Form(default=None),
    medication_category: str | None = Form(default=None),
    medicationCategory: str | None = Form(default=None),
    is_prescription: bool = Form(default=True),
    notes: str | None = Form(default=None),
    ocr_text: str | None = Form(default=None),
) -> Medication:
    content = await file.read()
    if not content:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Uploaded file is empty")
    allowed_types = {"image/jpeg", "image/png", "image/webp", "application/pdf"}
    if file.content_type and file.content_type not in allowed_types:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Upload must be an image or PDF file")

    guessed_name = first_text_line(name, ocr_text, file.filename)
    medication = medication_from_parts(
        user_id=current_user.id,
        name=guessed_name,
        active_ingredient=active_ingredient or activeIngredient,
        dosage=dosage,
        form=form.strip().lower() if form else "other",
        frequency=frequency,
        medication_category=medication_category or medicationCategory,
        is_prescription=is_prescription,
        notes=notes or f"Created from uploaded file: {file.filename or 'upload'}",
    )
    db.add(medication)
    db.flush()
    log_audit(
        db,
        current_user,
        "create_medication_from_upload",
        "medication",
        medication.id,
        {"filename": file.filename, "content_type": file.content_type, "size_bytes": len(content)},
    )
    db.commit()
    db.refresh(medication)
    return medication


@router.post("/camera", response_model=MedicationOut, status_code=status.HTTP_201_CREATED)
def create_medication_from_camera(
    payload: CameraMedicationCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> Medication:
    guessed_name = first_text_line(payload.name, payload.ocr_text, payload.file_name, "Camera medication")
    medication = medication_from_parts(
        user_id=current_user.id,
        name=guessed_name,
        active_ingredient=payload.active_ingredient,
        dosage=payload.dosage,
        form=payload.form.value if payload.form else "other",
        frequency=payload.frequency,
        medication_category=payload.medication_category,
        is_prescription=payload.is_prescription,
        notes=payload.notes or "Created from camera capture",
    )
    db.add(medication)
    db.flush()
    log_audit(
        db,
        current_user,
        "create_medication_from_camera",
        "medication",
        medication.id,
        {"file_name": payload.file_name, "content_type": payload.content_type},
    )
    db.commit()
    db.refresh(medication)
    return medication


@router.get("", response_model=list[MedicationOut])
def list_medications(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> list[Medication]:
    return list(db.scalars(select(Medication).where(Medication.user_id == current_user.id).order_by(Medication.name)))


@router.get("/history", response_model=MedicationHistoryResponse)
def medication_history(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> MedicationHistoryResponse:
    logs = list(
        db.scalars(
            select(MedicationLog)
            .where(MedicationLog.user_id == current_user.id)
            .order_by(MedicationLog.logged_at.desc())
        )
    )
    taken = [log for log in logs if log.status == ReminderStatus.taken]
    missed = [log for log in logs if log.status == ReminderStatus.missed]
    total_recorded = len(taken) + len(missed)
    adherence_rate = round((len(taken) / total_recorded) * 100, 2) if total_recorded else None
    return MedicationHistoryResponse(
        logs=logs,
        adherence_summary={
            "total_logs": len(logs),
            "taken": len(taken),
            "missed": len(missed),
            "adherence_rate_percent": adherence_rate,
        },
    )


@router.get("/{medication_id}", response_model=MedicationOut)
def get_medication(
    medication_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> Medication:
    return get_owned_medication(db, current_user, medication_id)


@router.put("/{medication_id}", response_model=MedicationOut)
def update_medication(
    medication_id: str,
    payload: MedicationUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> Medication:
    medication = get_manageable_medication(db, current_user, medication_id)
    data = payload.model_dump(exclude_unset=True)
    if data.get("form") is None:
        data.pop("form", None)
    if data.get("active_ingredient") == "":
        data["active_ingredient"] = data.get("name") or medication.name
    for field, value in data.items():
        setattr(medication, field, value)
    db.flush()
    log_audit(db, current_user, "update_medication", "medication", medication.id)
    db.commit()
    db.refresh(medication)
    return medication


@router.delete("/{medication_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_medication(
    medication_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> None:
    medication = get_manageable_medication(db, current_user, medication_id)
    log_audit(db, current_user, "delete_medication", "medication", medication.id)
    db.delete(medication)
    db.commit()
