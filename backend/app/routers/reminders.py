from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.database import get_db
from app.models import MedicationLog, Reminder, ReminderStatus, User, utc_now
from app.routers.helpers import get_manageable_medication
from app.schemas import MedicationLogOut, ReminderCreate, ReminderOut, ReminderUpdate
from app.services.audit import log_audit

router = APIRouter(prefix="/reminders", tags=["reminders"])


def reminder_to_out(reminder: Reminder, logs: list[MedicationLog] | None = None) -> ReminderOut:
    logs = logs or []
    return ReminderOut(
        id=reminder.id,
        user_id=reminder.user_id,
        medication_id=reminder.medication_id,
        medication_name=reminder.medication.name if reminder.medication else None,
        time=reminder.time,
        repeat_pattern=reminder.repeat_pattern,
        timezone=reminder.timezone,
        enabled=reminder.enabled,
        taken_status=any(log.status == ReminderStatus.taken for log in logs),
        missed_status=any(log.status == ReminderStatus.missed for log in logs),
        created_at=reminder.created_at,
    )


def get_owned_reminder(db: Session, current_user: User, reminder_id: str) -> Reminder:
    reminder = db.get(Reminder, reminder_id)
    if not reminder or reminder.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Reminder not found")
    return reminder


@router.post("", response_model=ReminderOut, status_code=status.HTTP_201_CREATED)
def create_reminder(
    payload: ReminderCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> ReminderOut:
    medication = get_manageable_medication(db, current_user, payload.medication_id)
    reminder = Reminder(
        user_id=medication.user_id,
        medication_id=medication.id,
        time=payload.time,
        repeat_pattern=payload.repeat_pattern,
        timezone=payload.timezone,
    )
    db.add(reminder)
    db.flush()
    log_audit(db, current_user, "create_reminder", "reminder", reminder.id)
    db.commit()
    db.refresh(reminder)
    return reminder_to_out(reminder)


@router.get("/today", response_model=list[ReminderOut])
def today_reminders(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> list[ReminderOut]:
    today = date.today()
    reminders = list(
        db.scalars(select(Reminder).where(Reminder.user_id == current_user.id, Reminder.enabled).order_by(Reminder.time))
    )
    outputs = []
    for reminder in reminders:
        logs = [
            log
            for log in reminder.logs
            if log.logged_at.date() == today
        ]
        outputs.append(reminder_to_out(reminder, logs))
    return outputs


@router.put("/{reminder_id}", response_model=ReminderOut)
def update_reminder(
    reminder_id: str,
    payload: ReminderUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> ReminderOut:
    reminder = get_owned_reminder(db, current_user, reminder_id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(reminder, field, value)
    db.flush()
    log_audit(db, current_user, "update_reminder", "reminder", reminder.id)
    db.commit()
    db.refresh(reminder)
    return reminder_to_out(reminder)


@router.delete("/{reminder_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_reminder(
    reminder_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> None:
    reminder = get_owned_reminder(db, current_user, reminder_id)
    log_audit(db, current_user, "delete_reminder", "reminder", reminder.id)
    db.delete(reminder)
    db.commit()


def mark_reminder(db: Session, current_user: User, reminder_id: str, status_value: ReminderStatus) -> MedicationLog:
    reminder = get_owned_reminder(db, current_user, reminder_id)
    log = MedicationLog(
        user_id=current_user.id,
        medication_id=reminder.medication_id,
        reminder_id=reminder.id,
        status=status_value,
        logged_at=utc_now(),
    )
    db.add(log)
    db.flush()
    log_audit(db, current_user, f"mark_reminder_{status_value.value}", "reminder", reminder.id)
    db.commit()
    db.refresh(log)
    return log


@router.post("/{reminder_id}/taken", response_model=MedicationLogOut)
def mark_taken(
    reminder_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> MedicationLog:
    return mark_reminder(db, current_user, reminder_id, ReminderStatus.taken)


@router.post("/{reminder_id}/missed", response_model=MedicationLogOut)
def mark_missed(
    reminder_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> MedicationLog:
    return mark_reminder(db, current_user, reminder_id, ReminderStatus.missed)
