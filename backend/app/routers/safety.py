from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.database import get_db
from app.models import HealthProfile, InteractionResult, Medication, Substance, Supplement, User
from app.rule_engine.engine import SafetyContext, analyze_safety
from app.schemas import InteractionHistoryOut, SafetyCheckResponse
from app.services.audit import log_audit

router = APIRouter(tags=["safety"])


def run_safety_check_for_user(db: Session, user_id: str) -> SafetyCheckResponse:
    profile = db.scalar(select(HealthProfile).where(HealthProfile.user_id == user_id))
    medications = list(db.scalars(select(Medication).where(Medication.user_id == user_id)))
    supplements = list(db.scalars(select(Supplement).where(Supplement.user_id == user_id)))
    substances = list(db.scalars(select(Substance).where(Substance.user_id == user_id, Substance.is_active)))
    return analyze_safety(
        db,
        SafetyContext(profile=profile, medications=medications, supplements=supplements, substances=substances),
    )


@router.post("/safety-check", response_model=SafetyCheckResponse)
def safety_check(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> SafetyCheckResponse:
    result = run_safety_check_for_user(db, current_user.id)
    record = InteractionResult(
        user_id=current_user.id,
        total_risk_score=result.total_risk_score,
        highest_severity=result.highest_severity,
        interactions=[interaction.model_dump(mode="json") for interaction in result.interactions],
        recommended_actions=result.recommended_actions,
        safe_timing_suggestions=result.safe_timing_suggestions,
        disclaimer=result.disclaimer,
    )
    db.add(record)
    db.flush()
    log_audit(db, current_user, "run_safety_check", "interaction_result", record.id)
    db.commit()
    return result


@router.get("/interactions/history", response_model=list[InteractionHistoryOut])
def interaction_history(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> list[InteractionResult]:
    return list(
        db.scalars(
            select(InteractionResult)
            .where(InteractionResult.user_id == current_user.id)
            .order_by(InteractionResult.created_at.desc())
        )
    )
