from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models import CaregiverAccess, User
from app.schemas import CaregiverAccessOut, CaregiverShareCreate

router = APIRouter()


@router.post("/share", response_model=CaregiverAccessOut, status_code=status.HTTP_201_CREATED)
def share_with_caregiver(
    payload: CaregiverShareCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> CaregiverAccess:
    caregiver = db.scalar(select(User).where(User.email == payload.caregiver_email.lower()))
    if not caregiver:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Caregiver user must register first")
    if caregiver.id == current_user.id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot share with yourself")

    existing = db.scalar(
        select(CaregiverAccess).where(
            CaregiverAccess.patient_id == current_user.id,
            CaregiverAccess.caregiver_id == caregiver.id,
        )
    )
    if existing:
        existing.relationship = payload.relationship
        existing.can_edit = payload.can_edit
        db.commit()
        db.refresh(existing)
        return existing

    access = CaregiverAccess(
        patient_id=current_user.id,
        caregiver_id=caregiver.id,
        relationship=payload.relationship,
        can_edit=payload.can_edit,
    )
    db.add(access)
    db.commit()
    db.refresh(access)
    return access


@router.get("", response_model=list[CaregiverAccessOut])
def list_caregivers(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> list[CaregiverAccess]:
    return list(db.scalars(select(CaregiverAccess).where(CaregiverAccess.patient_id == current_user.id)))
