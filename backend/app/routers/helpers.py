from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.auth.dependencies import can_access_patient
from app.models import Medication, Substance, Supplement, User


def get_owned_medication(db: Session, current_user: User, medication_id: str) -> Medication:
    medication = db.get(Medication, medication_id)
    if not medication or not can_access_patient(db, current_user, medication.user_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Medication not found")
    return medication


def get_manageable_medication(db: Session, current_user: User, medication_id: str) -> Medication:
    medication = db.get(Medication, medication_id)
    if not medication or not can_access_patient(db, current_user, medication.user_id, require_manage=True):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Medication not found")
    return medication


def get_owned_supplement(db: Session, current_user: User, supplement_id: str) -> Supplement:
    supplement = db.get(Supplement, supplement_id)
    if not supplement or supplement.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Supplement not found")
    return supplement


def get_owned_substance(db: Session, current_user: User, substance_id: str) -> Substance:
    substance = db.get(Substance, substance_id)
    if not substance or substance.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Substance not found")
    return substance
