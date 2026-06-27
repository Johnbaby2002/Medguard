from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.database import get_db
from app.models import Medication, MedicationScan, ScanStatus, ScanType, User
from app.schemas import (
    BarcodeScanRequest,
    CameraScanRequest,
    MedicationDraftOut,
    MedicationFromScanCreate,
    MedicationOut,
    MedicationScanOut,
    PrescriptionOCRDraftRequest,
)
from app.services.audit import log_audit

router = APIRouter(prefix="/scans", tags=["scan intake"])


def build_medication_draft(
    name: str | None,
    active_ingredient: str | None,
    dosage: str | None,
    notes: str | None,
    is_prescription: bool = True,
) -> MedicationDraftOut:
    resolved_name = name or "Unknown medication"
    return MedicationDraftOut(
        name=resolved_name,
        active_ingredient=active_ingredient or resolved_name,
        dosage=dosage or "confirm with package or prescription",
        frequency="confirm with label",
        medication_category=None,
        is_prescription=is_prescription,
        notes=notes,
    )


def draft_from_text(text: str, notes: str, is_prescription: bool) -> MedicationDraftOut:
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    first_line = lines[0] if lines else "Unknown medication"
    second_line = lines[1] if len(lines) > 1 else None
    return build_medication_draft(first_line, first_line, second_line, notes, is_prescription=is_prescription)


@router.post("/barcode", response_model=MedicationScanOut, status_code=status.HTTP_201_CREATED)
def create_barcode_scan(
    payload: BarcodeScanRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> MedicationScan:
    draft = build_medication_draft(
        payload.product_name,
        payload.active_ingredient,
        payload.dosage,
        payload.notes or f"Barcode captured: {payload.barcode}",
        is_prescription=False,
    )
    scan = MedicationScan(
        user_id=current_user.id,
        scan_type=ScanType.barcode,
        raw_value=payload.barcode,
        status=ScanStatus.matched if payload.product_name else ScanStatus.needs_review,
        confidence=70 if payload.product_name else 20,
        medication_draft=draft.model_dump(mode="json"),
    )
    db.add(scan)
    db.flush()
    log_audit(db, current_user, "create_barcode_scan", "medication_scan", scan.id)
    db.commit()
    db.refresh(scan)
    return scan


@router.post("/camera", response_model=MedicationScanOut, status_code=status.HTTP_201_CREATED)
def create_camera_scan(
    payload: CameraScanRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> MedicationScan:
    draft = draft_from_text(
        payload.ocr_text or payload.file_name or "Camera medication image",
        "Camera capture received. Review fields before saving as a medication.",
        is_prescription=True,
    )
    scan = MedicationScan(
        user_id=current_user.id,
        scan_type=ScanType.camera,
        raw_value=payload.file_name or "camera-capture",
        status=ScanStatus.draft,
        confidence=25,
        medication_draft=draft.model_dump(mode="json"),
    )
    db.add(scan)
    db.flush()
    log_audit(
        db,
        current_user,
        "create_camera_scan",
        "medication_scan",
        scan.id,
        {"content_type": payload.content_type, "notes": payload.notes},
    )
    db.commit()
    db.refresh(scan)
    return scan


@router.post("/upload", response_model=MedicationScanOut, status_code=status.HTTP_201_CREATED)
async def create_upload_scan(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
    file: UploadFile = File(...),
    ocr_text: str | None = Form(default=None),
    notes: str | None = Form(default=None),
) -> MedicationScan:
    content = await file.read()
    if not content:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Uploaded file is empty")
    allowed_types = {"image/jpeg", "image/png", "image/webp", "application/pdf"}
    if file.content_type and file.content_type not in allowed_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Upload must be an image or PDF file",
        )
    draft = draft_from_text(
        ocr_text or file.filename or "Uploaded medication file",
        "Upload received. Review fields before saving as a medication.",
        is_prescription=True,
    )
    scan = MedicationScan(
        user_id=current_user.id,
        scan_type=ScanType.upload,
        raw_value=file.filename or "uploaded-file",
        status=ScanStatus.draft,
        confidence=30 if ocr_text else 15,
        medication_draft=draft.model_dump(mode="json"),
    )
    db.add(scan)
    db.flush()
    log_audit(
        db,
        current_user,
        "create_upload_scan",
        "medication_scan",
        scan.id,
        {"filename": file.filename, "content_type": file.content_type, "size_bytes": len(content), "notes": notes},
    )
    db.commit()
    db.refresh(scan)
    return scan


@router.post("/prescription-ocr", response_model=MedicationScanOut, status_code=status.HTTP_201_CREATED)
def create_prescription_ocr_draft(
    payload: PrescriptionOCRDraftRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> MedicationScan:
    lines = [line.strip() for line in payload.ocr_text.splitlines() if line.strip()]
    first_line = lines[0] if lines else "Unknown prescription"
    second_line = lines[1] if len(lines) > 1 else None
    draft = build_medication_draft(
        first_line,
        first_line,
        second_line,
        "Draft created from OCR text. Review all fields before saving as a medication.",
        is_prescription=True,
    )
    scan = MedicationScan(
        user_id=current_user.id,
        scan_type=ScanType.prescription_ocr,
        raw_value=payload.ocr_text,
        status=ScanStatus.draft,
        confidence=35,
        medication_draft=draft.model_dump(mode="json"),
    )
    db.add(scan)
    db.flush()
    log_audit(
        db,
        current_user,
        "create_prescription_ocr_draft",
        "medication_scan",
        scan.id,
        {"image_reference": payload.image_reference},
    )
    db.commit()
    db.refresh(scan)
    return scan


@router.post("/{scan_id}/medication", response_model=MedicationOut, status_code=status.HTTP_201_CREATED)
def create_medication_from_scan(
    scan_id: str,
    payload: MedicationFromScanCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> Medication:
    scan = db.get(MedicationScan, scan_id)
    if not scan or scan.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Scan not found")

    draft = scan.medication_draft or {}
    data = {
        "name": payload.name or draft.get("name") or "Unknown medication",
        "active_ingredient": payload.active_ingredient or draft.get("active_ingredient"),
        "dosage": payload.dosage or draft.get("dosage") or "confirm with label",
        "form": payload.form or draft.get("form") or "other",
        "frequency": payload.frequency or draft.get("frequency") or "as directed",
        "medication_category": payload.medication_category or draft.get("medication_category"),
        "is_prescription": payload.is_prescription
        if payload.is_prescription is not None
        else draft.get("is_prescription", True),
        "notes": payload.notes or draft.get("notes") or f"Created from scan {scan.id}",
    }
    data["active_ingredient"] = data["active_ingredient"] or data["name"]
    medication = Medication(user_id=current_user.id, **data)
    scan.status = ScanStatus.matched
    db.add(medication)
    db.flush()
    log_audit(db, current_user, "create_medication_from_scan", "medication", medication.id, {"scan_id": scan.id})
    db.commit()
    db.refresh(medication)
    return medication


@router.get("", response_model=list[MedicationScanOut])
def list_scans(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> list[MedicationScan]:
    return list(
        db.scalars(
            select(MedicationScan)
            .where(MedicationScan.user_id == current_user.id)
            .order_by(MedicationScan.created_at.desc())
        )
    )
