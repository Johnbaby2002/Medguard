from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models import DoctorReport, DoseLog, Medication, Reminder, User
from app.schemas import DoctorReportCreate, DoctorReportOut

router = APIRouter()


@router.post("/doctor", response_model=DoctorReportOut, status_code=status.HTTP_201_CREATED)
def create_doctor_report(
    payload: DoctorReportCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> DoctorReport:
    medications = list(db.scalars(select(Medication).where(Medication.owner_id == current_user.id)))
    dose_logs = list(
        db.scalars(select(DoseLog).where(DoseLog.owner_id == current_user.id).order_by(DoseLog.taken_at.desc()).limit(50))
    )
    reminders = list(
        db.scalars(select(Reminder).join(Medication).where(Medication.owner_id == current_user.id))
    )

    snapshot = {
        "patient": {
            "id": current_user.id,
            "full_name": current_user.full_name,
            "email": current_user.email,
            "date_of_birth": current_user.date_of_birth.isoformat() if current_user.date_of_birth else None,
            "emergency_contact": current_user.emergency_contact,
        },
        "medications": [
            {
                "name": med.name,
                "form": med.form,
                "strength": med.strength,
                "active_ingredients": med.active_ingredients,
                "prescribing_doctor": med.prescribing_doctor,
                "instructions": med.instructions,
                "is_active": med.is_active,
            }
            for med in medications
        ],
        "reminders": [
            {
                "medication_id": reminder.medication_id,
                "time_of_day": reminder.time_of_day,
                "dose_amount": reminder.dose_amount,
                "days_of_week": reminder.days_of_week,
                "enabled": reminder.enabled,
            }
            for reminder in reminders
        ],
        "recent_dose_logs": [
            {
                "medication_id": log.medication_id,
                "status": log.status.value,
                "taken_at": log.taken_at.isoformat(),
                "notes": log.notes,
            }
            for log in dose_logs
        ],
    }

    report = DoctorReport(owner_id=current_user.id, title=payload.title, summary=payload.summary, snapshot=snapshot)
    db.add(report)
    db.commit()
    db.refresh(report)
    return report


@router.get("/doctor", response_model=list[DoctorReportOut])
def list_doctor_reports(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> list[DoctorReport]:
    return list(
        db.scalars(
            select(DoctorReport).where(DoctorReport.owner_id == current_user.id).order_by(DoctorReport.created_at.desc())
        )
    )
