from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.database import get_db
from app.models import Medication, User
from app.routers.helpers import get_manageable_medication, get_owned_medication
from app.schemas import MedicationCreate, MedicationOut, MedicationUpdate
from app.services.audit import log_audit

router = APIRouter(prefix="/medications", tags=["medications"])


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


@router.get("", response_model=list[MedicationOut])
def list_medications(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> list[Medication]:
    return list(db.scalars(select(Medication).where(Medication.user_id == current_user.id).order_by(Medication.name)))


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
