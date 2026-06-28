from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.database import get_db
from app.models import User
from app.routers.ai import build_ai_safety_snapshot
from app.routers.safety import run_safety_check_for_user
from app.schemas import AssistantAskRequest, AssistantAskResponse, MEDICAL_DISCLAIMER
from app.services.ai_pipeline_adapter import ask_local_ai_pipeline, get_ai_pipeline_status
from app.services.audit import log_audit

router = APIRouter(prefix="/assistant", tags=["assistant"])


@router.get("/status")
def assistant_status(current_user: Annotated[User, Depends(get_current_user)]) -> dict:
    status = get_ai_pipeline_status()
    status["fallback"] = "rule_based_safety_engine"
    return status


@router.post("/ask", response_model=AssistantAskResponse)
def ask_assistant(
    payload: AssistantAskRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> AssistantAskResponse:
    safety = run_safety_check_for_user(db, current_user.id)
    snapshot = build_ai_safety_snapshot(db, current_user)
    question = payload.question.lower()
    related = [
        interaction
        for interaction in safety.interactions
        if any(term in question for term in ["alcohol", "ibuprofen", "pain", "risk", "why"])
        or any(item.lower() in question for item in interaction.matched_items)
    ]
    if not related:
        related = safety.interactions[:3]

    ai_result = ask_local_ai_pipeline(payload.question, snapshot)
    if ai_result and not ai_result.get("error"):
        answer = ai_result.get("answer") or ai_result.get("summary") or "The local AI pipeline returned a result."
        recommendation = (
            ai_result.get("recommendation")
            or ai_result.get("recommended_action")
            or "Review the warnings and ask a doctor or pharmacist before changing how you take medicines."
        )
        log_audit(db, current_user, "ask_local_ai_pipeline", "assistant", current_user.id)
    elif related:
        answer = "I found rule-based safety warnings that may be relevant to your question."
        recommendation = "Review the warnings and ask a doctor or pharmacist before changing how you take medicines."
    else:
        answer = "I did not find a rule-based warning for your current medication list, but labels and personal medical advice still matter."
        recommendation = "Follow the label and ask a doctor or pharmacist if you are unsure."
    log_audit(db, current_user, "ask_rule_based_assistant", "assistant", current_user.id)
    db.commit()
    return AssistantAskResponse(
        answer=answer,
        related_interactions=related,
        recommendation=recommendation,
        disclaimer=MEDICAL_DISCLAIMER,
    )
