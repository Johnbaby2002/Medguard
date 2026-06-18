from datetime import datetime, timezone
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models import Medication, SafetyCheck, SafetyCheckStatus, User
from app.schemas import SafetyCheckCreate, SafetyCheckOut, SafetyCheckResultUpdate

router = APIRouter()


def medication_snapshot(medication: Medication) -> dict:
    return {
        "id": medication.id,
        "name": medication.name,
        "form": medication.form,
        "strength": medication.strength,
        "active_ingredients": medication.active_ingredients,
        "instructions": medication.instructions,
        "is_active": medication.is_active,
    }


@router.post("/checks", response_model=SafetyCheckOut, status_code=status.HTTP_201_CREATED)
def create_safety_check(
    payload: SafetyCheckCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> SafetyCheck:
    query = select(Medication).where(Medication.owner_id == current_user.id)
    if payload.medication_ids:
        query = query.where(Medication.id.in_(payload.medication_ids))

    medications = list(db.scalars(query))
    if payload.medication_ids:
        found_ids = {medication.id for medication in medications}
        missing_ids = sorted(set(payload.medication_ids) - found_ids)
        if missing_ids:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"message": "Some medications were not found", "missing_medication_ids": missing_ids},
            )

    request_payload = {
        "user_id": current_user.id,
        "medications": [medication_snapshot(medication) for medication in medications],
        "context": payload.context,
    }
    check = SafetyCheck(owner_id=current_user.id, status=SafetyCheckStatus.pending, request_payload=request_payload)
    db.add(check)
    db.commit()
    db.refresh(check)
    return check


@router.get("/checks", response_model=list[SafetyCheckOut])
def list_safety_checks(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> list[SafetyCheck]:
    return list(
        db.scalars(
            select(SafetyCheck).where(SafetyCheck.owner_id == current_user.id).order_by(SafetyCheck.created_at.desc())
        )
    )


@router.patch("/checks/{check_id}/result", response_model=SafetyCheckOut)
def update_safety_check_result(
    check_id: str,
    payload: SafetyCheckResultUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> SafetyCheck:
    check = db.get(SafetyCheck, check_id)
    if not check or check.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Safety check not found")

    check.status = payload.status
    check.result_payload = payload.result_payload
    check.completed_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(check)
    return check
