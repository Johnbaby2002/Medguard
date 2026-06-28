from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.database import get_db
from app.models import Reminder, User
from app.schemas import AdherenceSummaryResponse
from app.services.schedule import adherence_from_reminders

router = APIRouter(prefix="/adherence", tags=["adherence"])


@router.get("/summary", response_model=AdherenceSummaryResponse)
def adherence_summary(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> dict:
    reminders = list(db.scalars(select(Reminder).where(Reminder.user_id == current_user.id, Reminder.enabled)))
    return adherence_from_reminders(reminders)
