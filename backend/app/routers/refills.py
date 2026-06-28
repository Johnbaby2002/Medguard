from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.database import get_db
from app.models import Medication, User
from app.schemas import MedicationOut

router = APIRouter(prefix="/refills", tags=["refills"])


@router.get("/due", response_model=list[MedicationOut])
def refills_due(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> list[Medication]:
    medications = list(db.scalars(select(Medication).where(Medication.user_id == current_user.id)))
    return [
        medication
        for medication in medications
        if medication.pills_remaining is not None
        and medication.refill_threshold is not None
        and medication.pills_remaining <= medication.refill_threshold
    ]
