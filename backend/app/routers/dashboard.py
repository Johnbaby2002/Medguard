from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.database import get_db
from app.models import InteractionResult, Medication, MedicationLog, Reminder, ReminderStatus, Supplement, User

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("")
def dashboard(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> dict:
    active_medications = db.scalar(
        select(func.count()).select_from(Medication).where(Medication.user_id == current_user.id)
    ) or 0
    supplements = db.scalar(
        select(func.count()).select_from(Supplement).where(Supplement.user_id == current_user.id)
    ) or 0
    active_reminders = db.scalar(
        select(func.count()).select_from(Reminder).where(Reminder.user_id == current_user.id, Reminder.enabled)
    ) or 0
    taken_doses = db.scalar(
        select(func.count())
        .select_from(MedicationLog)
        .where(MedicationLog.user_id == current_user.id, MedicationLog.status == ReminderStatus.taken)
    ) or 0
    missed_doses = db.scalar(
        select(func.count())
        .select_from(MedicationLog)
        .where(MedicationLog.user_id == current_user.id, MedicationLog.status == ReminderStatus.missed)
    ) or 0
    latest_risk = db.scalar(
        select(InteractionResult)
        .where(InteractionResult.user_id == current_user.id)
        .order_by(InteractionResult.created_at.desc())
        .limit(1)
    )
    return {
        "active_medications": active_medications,
        "supplements": supplements,
        "active_reminders": active_reminders,
        "taken_doses": taken_doses,
        "missed_doses": missed_doses,
        "latest_total_risk_score": latest_risk.total_risk_score if latest_risk else 0,
        "latest_highest_severity": latest_risk.highest_severity.value if latest_risk and latest_risk.highest_severity else None,
    }
