from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.database import get_db
from app.models import Reminder, User
from app.schemas import TimelineItem, TimelineTodayResponse
from app.services.schedule import status_for_reminder

router = APIRouter(prefix="/timeline", tags=["timeline"])


def bucket_for_time(value: str) -> str:
    hour = int(value.split(":")[0])
    if 5 <= hour < 12:
        return "morning"
    if 12 <= hour < 17:
        return "afternoon"
    if 17 <= hour < 21:
        return "evening"
    return "night"


@router.get("/today", response_model=TimelineTodayResponse)
def timeline_today(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> TimelineTodayResponse:
    today = date.today()
    reminders = list(
        db.scalars(select(Reminder).where(Reminder.user_id == current_user.id, Reminder.enabled).order_by(Reminder.time))
    )
    grouped = TimelineTodayResponse()
    for reminder in reminders:
        item = TimelineItem(
            medication_name=reminder.medication.name if reminder.medication else "Medication",
            dose=reminder.medication.dosage if reminder.medication else "",
            time=reminder.time,
            status=status_for_reminder(reminder, today),
        )
        getattr(grouped, bucket_for_time(reminder.time)).append(item)
    return grouped
