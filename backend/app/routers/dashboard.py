from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.database import get_db
from app.models import InteractionResult, Medication, MedicationLog, Reminder, ReminderStatus, Substance, Supplement, User
from app.routers.safety import run_safety_check_for_user
from app.schemas import RiskSummaryResponse
from app.services.schedule import adherence_from_reminders, status_for_reminder

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


def adherence_percent(logs: list[MedicationLog]) -> float | None:
    taken = [log for log in logs if log.status == ReminderStatus.taken]
    missed = [log for log in logs if log.status == ReminderStatus.missed]
    total = len(taken) + len(missed)
    return round((len(taken) / total) * 100, 2) if total else None


def build_dashboard_summary(current_user: User, db: Session) -> dict:
    today = date.today()
    medications = list(db.scalars(select(Medication).where(Medication.user_id == current_user.id)))
    supplements = list(db.scalars(select(Supplement).where(Supplement.user_id == current_user.id)))
    substances = list(db.scalars(select(Substance).where(Substance.user_id == current_user.id, Substance.is_active)))
    reminders = list(
        db.scalars(select(Reminder).where(Reminder.user_id == current_user.id, Reminder.enabled).order_by(Reminder.time))
    )
    logs = list(db.scalars(select(MedicationLog).where(MedicationLog.user_id == current_user.id)))
    today_logs = [log for log in logs if log.logged_at.date() == today]
    missed_today = [log for log in today_logs if log.status == ReminderStatus.missed]
    next_reminder = reminders[0] if reminders else None
    safety = run_safety_check_for_user(db, current_user.id)
    return {
        "total_medications": len(medications),
        "total_supplements": len(supplements),
        "total_substances": len(substances),
        "active_reminders_today": len(reminders),
        "missed_doses_today": len(missed_today),
        "highest_current_risk_level": safety.highest_severity.value,
        "detected_interactions": len(safety.interactions),
        "next_medication_reminder": {
            "id": next_reminder.id,
            "time": next_reminder.time,
            "medication_id": next_reminder.medication_id,
            "medication_name": next_reminder.medication.name if next_reminder.medication else None,
        }
        if next_reminder
        else None,
        "adherence_percentage": adherence_percent(logs),
    }


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


@router.get("/summary")
def dashboard_summary(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> dict:
    return build_dashboard_summary(current_user, db)


@router.get("/risk-summary", response_model=RiskSummaryResponse)
def dashboard_risk_summary(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> RiskSummaryResponse:
    today = date.today()
    medications = list(db.scalars(select(Medication).where(Medication.user_id == current_user.id)))
    supplements = list(db.scalars(select(Supplement).where(Supplement.user_id == current_user.id)))
    substances = list(db.scalars(select(Substance).where(Substance.user_id == current_user.id, Substance.is_active)))
    reminders = list(
        db.scalars(select(Reminder).where(Reminder.user_id == current_user.id, Reminder.enabled).order_by(Reminder.time))
    )
    safety = run_safety_check_for_user(db, current_user.id)
    adherence = adherence_from_reminders(reminders)
    missed_today = sum(1 for reminder in reminders if status_for_reminder(reminder, today) == ReminderStatus.missed)
    next_reminder = next((reminder for reminder in reminders if status_for_reminder(reminder, today) == ReminderStatus.pending), None)
    return RiskSummaryResponse(
        total_medications=len(medications),
        total_supplements=len(supplements),
        total_substances=len(substances),
        total_interactions=len(safety.interactions),
        highest_risk_level=safety.highest_severity,
        risk_score_0_to_100=safety.total_risk_score,
        missed_doses_today=missed_today,
        adherence_percentage=adherence["adherence_percentage"],
        next_reminder={
            "id": next_reminder.id,
            "time": next_reminder.time,
            "medication_id": next_reminder.medication_id,
            "medication_name": next_reminder.medication.name if next_reminder.medication else None,
        }
        if next_reminder
        else None,
        top_3_warnings=safety.interactions[:3],
        disclaimer=safety.disclaimer,
    )
