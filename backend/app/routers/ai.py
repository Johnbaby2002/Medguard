from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.database import get_db
from app.models import AIReviewStatus, AISafetyReview, HealthProfile, Medication, Substance, Supplement, User
from app.routers.safety import run_safety_check_for_user
from app.schemas import AISafetyReviewCreate, AISafetyReviewOut, AISafetyReviewResultUpdate
from app.services.audit import log_audit

router = APIRouter(prefix="/ai", tags=["ai handoff"])


def build_ai_safety_snapshot(db: Session, user: User) -> dict:
    profile = db.scalar(select(HealthProfile).where(HealthProfile.user_id == user.id))
    medications = list(db.scalars(select(Medication).where(Medication.user_id == user.id).order_by(Medication.name)))
    supplements = list(db.scalars(select(Supplement).where(Supplement.user_id == user.id).order_by(Supplement.name)))
    substances = list(db.scalars(select(Substance).where(Substance.user_id == user.id).order_by(Substance.name)))
    rule_result = run_safety_check_for_user(db, user.id)
    return {
        "user": {"id": user.id, "age": profile.age if profile else None, "sex": profile.sex.value if profile and profile.sex else None},
        "profile": {
            "known_conditions": profile.known_conditions if profile else [],
            "allergies": profile.allergies if profile else [],
            "pregnancy_status": profile.pregnancy_status if profile else None,
            "alcohol_use": profile.alcohol_use if profile else None,
            "caffeine_preworkout_use": profile.caffeine_preworkout_use if profile else None,
        },
        "medications": [
            {
                "id": medication.id,
                "name": medication.name,
                "active_ingredient": medication.active_ingredient,
                "dosage": medication.dosage,
                "frequency": medication.frequency,
                "category": medication.medication_category,
                "is_prescription": medication.is_prescription,
            }
            for medication in medications
        ],
        "supplements": [
            {
                "id": supplement.id,
                "name": supplement.name,
                "active_ingredient_category": supplement.active_ingredient_category,
                "dose": supplement.dose,
                "frequency": supplement.frequency,
            }
            for supplement in supplements
        ],
        "substances": [
            {
                "id": substance.id,
                "name": substance.name,
                "category": substance.category.value,
                "active_ingredient": substance.active_ingredient,
                "frequency": substance.frequency,
                "amount": substance.amount,
                "is_active": substance.is_active,
            }
            for substance in substances
        ],
        "rule_based_safety_result": rule_result.model_dump(mode="json"),
        "instructions": [
            "Do not diagnose diseases.",
            "Return interaction explanations in plain language.",
            "Always include the medical disclaimer.",
            "Flag uncertainty instead of inventing clinical facts.",
        ],
    }


@router.post("/safety-checks", response_model=AISafetyReviewOut, status_code=status.HTTP_201_CREATED)
def create_ai_safety_review(
    payload: AISafetyReviewCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> AISafetyReview:
    review = AISafetyReview(
        user_id=current_user.id,
        status=AIReviewStatus.pending,
        request_source=payload.request_source,
        input_snapshot=build_ai_safety_snapshot(db, current_user),
    )
    db.add(review)
    db.flush()
    log_audit(db, current_user, "create_ai_safety_review", "ai_safety_review", review.id)
    db.commit()
    db.refresh(review)
    return review


@router.get("/safety-checks/pending", response_model=list[AISafetyReviewOut])
def list_pending_ai_safety_reviews(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> list[AISafetyReview]:
    return list(
        db.scalars(
            select(AISafetyReview)
            .where(AISafetyReview.user_id == current_user.id, AISafetyReview.status == AIReviewStatus.pending)
            .order_by(AISafetyReview.created_at)
        )
    )


@router.get("/safety-checks/{review_id}", response_model=AISafetyReviewOut)
def get_ai_safety_review(
    review_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> AISafetyReview:
    review = db.get(AISafetyReview, review_id)
    if not review or review.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="AI safety review not found")
    return review


@router.put("/safety-checks/{review_id}/result", response_model=AISafetyReviewOut)
def submit_ai_safety_review_result(
    review_id: str,
    payload: AISafetyReviewResultUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> AISafetyReview:
    review = db.get(AISafetyReview, review_id)
    if not review or review.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="AI safety review not found")
    review.status = payload.status
    review.ai_result = payload.ai_result
    review.error_message = payload.error_message
    db.flush()
    log_audit(db, current_user, "submit_ai_safety_review_result", "ai_safety_review", review.id)
    db.commit()
    db.refresh(review)
    return review
