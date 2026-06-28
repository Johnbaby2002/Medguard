from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth.dependencies import can_access_patient, get_current_user
from app.database import get_db
from app.models import CaregiverAccess, HealthProfile, Medication, MedicationLog, Reminder, ReminderStatus, Supplement, User
from app.routers.reminders import reminder_to_out
from app.routers.reports import medication_summary
from app.schemas import (
    CaregiverAccessOut,
    CaregiverInvite,
    MedicationLogOut,
    MedicationOut,
    MedicationSummaryReport,
    ReminderOut,
    UserOut,
)
from app.services.audit import log_audit

router = APIRouter(prefix="/caregiver", tags=["caregiver"])


@router.post("/invite", response_model=CaregiverAccessOut, status_code=status.HTTP_201_CREATED)
def invite_caregiver(
    payload: CaregiverInvite,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> CaregiverAccess:
    caregiver = db.scalar(select(User).where(User.email == payload.caregiver_email.lower()))
    if not caregiver:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Caregiver must register first")
    if caregiver.id == current_user.id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot invite yourself")

    access = db.scalar(
        select(CaregiverAccess).where(
            CaregiverAccess.patient_id == current_user.id,
            CaregiverAccess.caregiver_id == caregiver.id,
        )
    )
    if not access:
        access = CaregiverAccess(patient_id=current_user.id, caregiver_id=caregiver.id)
        db.add(access)
    access.relationship = payload.relationship
    access.can_manage = payload.can_manage
    access.missed_dose_alerts = payload.missed_dose_alerts
    db.flush()
    log_audit(db, current_user, "invite_caregiver", "caregiver_access", access.id)
    db.commit()
    db.refresh(access)
    return access


@router.get("/patients", response_model=list[UserOut])
def caregiver_patients(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> list[User]:
    access_rows = list(db.scalars(select(CaregiverAccess).where(CaregiverAccess.caregiver_id == current_user.id)))
    if not access_rows:
        return []
    patient_ids = [row.patient_id for row in access_rows]
    return list(db.scalars(select(User).where(User.id.in_(patient_ids))))


@router.get("/patients/{patient_id}/medications", response_model=list[MedicationOut])
def caregiver_patient_medications(
    patient_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> list[Medication]:
    if not can_access_patient(db, current_user, patient_id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No caregiver access for this patient")
    return list(db.scalars(select(Medication).where(Medication.user_id == patient_id).order_by(Medication.name)))


@router.get("/patients/{patient_id}/reminders", response_model=list[ReminderOut])
def caregiver_patient_reminders(
    patient_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> list[ReminderOut]:
    if not can_access_patient(db, current_user, patient_id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No caregiver access for this patient")
    reminders = list(db.scalars(select(Reminder).where(Reminder.user_id == patient_id).order_by(Reminder.time)))
    return [reminder_to_out(reminder) for reminder in reminders]


@router.get("/patients/{patient_id}/missed-doses", response_model=list[MedicationLogOut])
def caregiver_patient_missed_doses(
    patient_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> list[MedicationLog]:
    if not can_access_patient(db, current_user, patient_id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No caregiver access for this patient")
    return list(
        db.scalars(
            select(MedicationLog)
            .where(MedicationLog.user_id == patient_id, MedicationLog.status == ReminderStatus.missed)
            .order_by(MedicationLog.logged_at.desc())
        )
    )


@router.get("/patients/{patient_id}/report", response_model=MedicationSummaryReport)
def caregiver_patient_report(
    patient_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> MedicationSummaryReport:
    if not can_access_patient(db, current_user, patient_id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No caregiver access for this patient")
    patient = db.get(User, patient_id)
    if not patient:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient not found")
    return medication_summary(patient, db)
