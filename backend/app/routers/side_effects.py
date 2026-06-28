from collections import Counter
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.database import get_db
from app.models import Medication, SideEffectLog, User, utc_now
from app.schemas import SideEffectLogCreate, SideEffectLogOut, SideEffectSummaryResponse
from app.services.audit import log_audit

router = APIRouter(prefix="/side-effects", tags=["side effects"])


@router.post("", response_model=SideEffectLogOut, status_code=status.HTTP_201_CREATED)
def create_side_effect(
    payload: SideEffectLogCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> SideEffectLog:
    if payload.medication_id:
        medication = db.get(Medication, payload.medication_id)
        if not medication or medication.user_id != current_user.id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Medication not found")
    log = SideEffectLog(
        user_id=current_user.id,
        symptom=payload.symptom,
        severity=payload.severity,
        started_at=payload.started_at or utc_now(),
        medication_id=payload.medication_id,
        notes=payload.notes,
    )
    db.add(log)
    db.flush()
    log_audit(db, current_user, "create_side_effect_log", "side_effect_log", log.id)
    db.commit()
    db.refresh(log)
    return log


@router.get("", response_model=list[SideEffectLogOut])
def list_side_effects(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> list[SideEffectLog]:
    return list(
        db.scalars(
            select(SideEffectLog)
            .where(SideEffectLog.user_id == current_user.id)
            .order_by(SideEffectLog.started_at.desc())
        )
    )


@router.get("/summary", response_model=SideEffectSummaryResponse)
def side_effect_summary(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> SideEffectSummaryResponse:
    logs = list(db.scalars(select(SideEffectLog).where(SideEffectLog.user_id == current_user.id)))
    counts = Counter(log.symptom.lower() for log in logs)
    grouped = [
        {
            "symptom": symptom,
            "frequency": frequency,
            "severities": Counter(log.severity.value for log in logs if log.symptom.lower() == symptom),
        }
        for symptom, frequency in counts.most_common()
    ]
    return SideEffectSummaryResponse(total_logs=len(logs), grouped_symptoms=grouped)
