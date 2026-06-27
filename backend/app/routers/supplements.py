from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.database import get_db
from app.models import Supplement, User
from app.routers.helpers import get_owned_supplement
from app.schemas import SupplementCreate, SupplementOut, SupplementUpdate
from app.services.audit import log_audit

router = APIRouter(prefix="/supplements", tags=["supplements"])


@router.post("", response_model=SupplementOut, status_code=status.HTTP_201_CREATED)
def create_supplement(
    payload: SupplementCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> Supplement:
    supplement = Supplement(user_id=current_user.id, **payload.model_dump())
    db.add(supplement)
    db.flush()
    log_audit(db, current_user, "create_supplement", "supplement", supplement.id)
    db.commit()
    db.refresh(supplement)
    return supplement


@router.get("", response_model=list[SupplementOut])
def list_supplements(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> list[Supplement]:
    return list(db.scalars(select(Supplement).where(Supplement.user_id == current_user.id).order_by(Supplement.name)))


@router.get("/{supplement_id}", response_model=SupplementOut)
def get_supplement(
    supplement_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> Supplement:
    return get_owned_supplement(db, current_user, supplement_id)


@router.put("/{supplement_id}", response_model=SupplementOut)
def update_supplement(
    supplement_id: str,
    payload: SupplementUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> Supplement:
    supplement = get_owned_supplement(db, current_user, supplement_id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(supplement, field, value)
    db.flush()
    log_audit(db, current_user, "update_supplement", "supplement", supplement.id)
    db.commit()
    db.refresh(supplement)
    return supplement


@router.delete("/{supplement_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_supplement(
    supplement_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> None:
    supplement = get_owned_supplement(db, current_user, supplement_id)
    log_audit(db, current_user, "delete_supplement", "supplement", supplement.id)
    db.delete(supplement)
    db.commit()
