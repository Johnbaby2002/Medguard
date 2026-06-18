from datetime import datetime, timezone
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.api.routes.medications import get_owned_medication
from app.db.session import get_db
from app.models import DoseLog, Reminder, User
from app.schemas import DoseLogCreate, DoseLogOut

router = APIRouter()


@router.post("", response_model=DoseLogOut, status_code=status.HTTP_201_CREATED)
def create_dose_log(
    payload: DoseLogCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> DoseLog:
    medication = get_owned_medication(db, current_user, payload.medication_id)

    if payload.reminder_id:
        reminder = db.get(Reminder, payload.reminder_id)
        if not reminder or reminder.medication_id != medication.id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Reminder not found")

    log = DoseLog(
        owner_id=current_user.id,
        medication_id=medication.id,
        reminder_id=payload.reminder_id,
        status=payload.status,
        taken_at=payload.taken_at or datetime.now(timezone.utc),
        notes=payload.notes,
    )
    db.add(log)
    db.commit()
    db.refresh(log)
    return log


@router.get("", response_model=list[DoseLogOut])
def list_dose_logs(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> list[DoseLog]:
    return list(
        db.scalars(
            select(DoseLog).where(DoseLog.owner_id == current_user.id).order_by(DoseLog.taken_at.desc())
        )
    )
