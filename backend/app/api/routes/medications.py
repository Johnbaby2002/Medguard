from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models import Medication, Reminder, User
from app.schemas import (
    MedicationCreate,
    MedicationFromScan,
    MedicationOut,
    MedicationUpdate,
    ReminderCreate,
    ReminderOut,
    ReminderUpdate,
)

router = APIRouter()


def get_owned_medication(db: Session, current_user: User, medication_id: str) -> Medication:
    medication = db.get(Medication, medication_id)
    if not medication or medication.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Medication not found")
    return medication


def get_owned_reminder(db: Session, current_user: User, reminder_id: str) -> Reminder:
    reminder = db.get(Reminder, reminder_id)
    if not reminder or reminder.medication.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Reminder not found")
    return reminder


@router.get("/medications", response_model=list[MedicationOut])
def list_medications(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> list[Medication]:
    return list(db.scalars(select(Medication).where(Medication.owner_id == current_user.id).order_by(Medication.name)))


@router.post("/medications", response_model=MedicationOut, status_code=status.HTTP_201_CREATED)
def create_medication(
    payload: MedicationCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> Medication:
    medication = Medication(owner_id=current_user.id, **payload.model_dump())
    db.add(medication)
    db.commit()
    db.refresh(medication)
    return medication


@router.post("/medications/from-scan", response_model=MedicationOut, status_code=status.HTTP_201_CREATED)
def create_medication_from_scan(
    payload: MedicationFromScan,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> Medication:
    medication = Medication(owner_id=current_user.id, **payload.model_dump())
    db.add(medication)
    db.commit()
    db.refresh(medication)
    return medication


@router.get("/medications/{medication_id}", response_model=MedicationOut)
def get_medication(
    medication_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> Medication:
    return get_owned_medication(db, current_user, medication_id)


@router.patch("/medications/{medication_id}", response_model=MedicationOut)
def update_medication(
    medication_id: str,
    payload: MedicationUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> Medication:
    medication = get_owned_medication(db, current_user, medication_id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(medication, field, value)
    db.commit()
    db.refresh(medication)
    return medication


@router.delete("/medications/{medication_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_medication(
    medication_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> None:
    medication = get_owned_medication(db, current_user, medication_id)
    db.delete(medication)
    db.commit()


@router.post("/medications/{medication_id}/reminders", response_model=ReminderOut, status_code=status.HTTP_201_CREATED)
def create_reminder(
    medication_id: str,
    payload: ReminderCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> ReminderOut:
    medication = get_owned_medication(db, current_user, medication_id)
    reminder = Reminder(medication_id=medication.id, **payload.model_dump())
    db.add(reminder)
    db.commit()
    db.refresh(reminder)
    return ReminderOut.model_validate(reminder).model_copy(update={"medication_name": medication.name})


@router.get("/reminders", response_model=list[ReminderOut])
def list_reminders(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> list[ReminderOut]:
    reminders = db.scalars(
        select(Reminder)
        .join(Medication)
        .where(Medication.owner_id == current_user.id)
        .order_by(Reminder.time_of_day)
    )
    return [
        ReminderOut.model_validate(reminder).model_copy(update={"medication_name": reminder.medication.name})
        for reminder in reminders
    ]


@router.patch("/reminders/{reminder_id}", response_model=ReminderOut)
def update_reminder(
    reminder_id: str,
    payload: ReminderUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> ReminderOut:
    reminder = get_owned_reminder(db, current_user, reminder_id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(reminder, field, value)
    db.commit()
    db.refresh(reminder)
    return ReminderOut.model_validate(reminder).model_copy(update={"medication_name": reminder.medication.name})


@router.delete("/reminders/{reminder_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_reminder(
    reminder_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> None:
    reminder = get_owned_reminder(db, current_user, reminder_id)
    db.delete(reminder)
    db.commit()
