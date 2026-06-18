from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models import DoseLog, DoseStatus, Medication, Reminder, SafetyCheck, User
from app.schemas import DashboardOut

router = APIRouter()


@router.get("", response_model=DashboardOut)
def dashboard(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> DashboardOut:
    active_medications = db.scalar(
        select(func.count()).select_from(Medication).where(Medication.owner_id == current_user.id, Medication.is_active)
    ) or 0
    active_reminders = db.scalar(
        select(func.count())
        .select_from(Reminder)
        .join(Medication)
        .where(Medication.owner_id == current_user.id, Reminder.enabled)
    ) or 0
    taken_doses = db.scalar(
        select(func.count()).select_from(DoseLog).where(DoseLog.owner_id == current_user.id, DoseLog.status == DoseStatus.taken)
    ) or 0
    missed_doses = db.scalar(
        select(func.count()).select_from(DoseLog).where(DoseLog.owner_id == current_user.id, DoseLog.status == DoseStatus.missed)
    ) or 0
    recent_safety_checks = list(
        db.scalars(
            select(SafetyCheck).where(SafetyCheck.owner_id == current_user.id).order_by(SafetyCheck.created_at.desc()).limit(5)
        )
    )

    return DashboardOut(
        active_medications=active_medications,
        active_reminders=active_reminders,
        taken_doses=taken_doses,
        missed_doses=missed_doses,
        recent_safety_checks=recent_safety_checks,
    )
