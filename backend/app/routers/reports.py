from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.database import get_db
from app.models import HealthProfile, Medication, MedicationLog, ReminderStatus, Supplement, User
from app.routers.safety import run_safety_check_for_user
from app.schemas import MedicationSummaryReport
from app.services.audit import log_audit

router = APIRouter(prefix="/reports", tags=["reports"])


@router.get("/medication-summary", response_model=MedicationSummaryReport)
def medication_summary(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> MedicationSummaryReport:
    profile = db.scalar(select(HealthProfile).where(HealthProfile.user_id == current_user.id))
    medications = list(db.scalars(select(Medication).where(Medication.user_id == current_user.id)))
    supplements = list(db.scalars(select(Supplement).where(Supplement.user_id == current_user.id)))
    logs = list(db.scalars(select(MedicationLog).where(MedicationLog.user_id == current_user.id)))
    missed = [log for log in logs if log.status == ReminderStatus.missed]
    taken = [log for log in logs if log.status == ReminderStatus.taken]
    risks = run_safety_check_for_user(db, current_user.id)
    notes = [
        "Bring this medication list to doctor or pharmacist visits.",
        "Review high or critical warnings with a healthcare professional.",
    ]
    log_audit(db, current_user, "generate_medication_summary", "report", current_user.id)
    db.commit()
    return MedicationSummaryReport(
        user_profile_summary={
            "user_id": current_user.id,
            "name": current_user.full_name,
            "email": current_user.email,
            "age": profile.age if profile else None,
            "sex": profile.sex.value if profile and profile.sex else None,
            "known_conditions": profile.known_conditions if profile else [],
            "allergies": profile.allergies if profile else [],
        },
        current_medications=medications,
        supplements=supplements,
        detected_risks=risks,
        adherence_summary={
            "total_logs": len(logs),
            "taken": len(taken),
            "missed": len(missed),
        },
        missed_doses=missed,
        doctor_pharmacist_notes=notes,
    )
