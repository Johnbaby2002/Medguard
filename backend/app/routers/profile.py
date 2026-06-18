from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.database import get_db
from app.models import HealthProfile, User
from app.schemas import HealthProfileOut, HealthProfileUpsert
from app.services.audit import log_audit

router = APIRouter(prefix="/profile", tags=["profile"])


@router.get("", response_model=HealthProfileOut)
def get_profile(current_user: Annotated[User, Depends(get_current_user)], db: Annotated[Session, Depends(get_db)]) -> HealthProfile:
    profile = current_user.health_profile
    if not profile:
        profile = HealthProfile(user_id=current_user.id)
        db.add(profile)
        db.flush()
        log_audit(db, current_user, "create_empty_profile", "health_profile", profile.id)
        db.commit()
        db.refresh(profile)
    return profile


@router.put("", response_model=HealthProfileOut)
def upsert_profile(
    payload: HealthProfileUpsert,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> HealthProfile:
    profile = current_user.health_profile
    if not profile:
        profile = HealthProfile(user_id=current_user.id)
        db.add(profile)
    for field, value in payload.model_dump().items():
        setattr(profile, field, value)
    db.flush()
    log_audit(db, current_user, "upsert_profile", "health_profile", profile.id)
    db.commit()
    db.refresh(profile)
    return profile
