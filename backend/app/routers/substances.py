from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.database import get_db
from app.models import Substance, User
from app.routers.helpers import get_owned_substance
from app.schemas import SubstanceCreate, SubstanceOut, SubstanceUpdate
from app.services.audit import log_audit

router = APIRouter(prefix="/substances", tags=["substances"])


@router.post("", response_model=SubstanceOut, status_code=status.HTTP_201_CREATED)
def create_substance(
    payload: SubstanceCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> Substance:
    substance = Substance(user_id=current_user.id, **payload.model_dump())
    db.add(substance)
    db.flush()
    log_audit(db, current_user, "create_substance", "substance", substance.id)
    db.commit()
    db.refresh(substance)
    return substance


@router.get("", response_model=list[SubstanceOut])
def list_substances(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> list[Substance]:
    return list(
        db.scalars(
            select(Substance)
            .where(Substance.user_id == current_user.id)
            .order_by(Substance.is_active.desc(), Substance.category, Substance.name)
        )
    )


@router.put("/{substance_id}", response_model=SubstanceOut)
def update_substance(
    substance_id: str,
    payload: SubstanceUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> Substance:
    substance = get_owned_substance(db, current_user, substance_id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(substance, field, value)
    db.flush()
    log_audit(db, current_user, "update_substance", "substance", substance.id)
    db.commit()
    db.refresh(substance)
    return substance


@router.delete("/{substance_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_substance(
    substance_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> None:
    substance = get_owned_substance(db, current_user, substance_id)
    log_audit(db, current_user, "delete_substance", "substance", substance.id)
    db.delete(substance)
    db.commit()
