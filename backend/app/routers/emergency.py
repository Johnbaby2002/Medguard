from datetime import datetime, timezone
from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.database import get_db
from app.models import HealthProfile, Medication, Severity, Substance, User
from app.routers.safety import run_safety_check_for_user
from app.schemas import EmergencyMedicationCard
from app.services.audit import log_audit

router = APIRouter(prefix="/emergency-card", tags=["emergency card"])


@router.get("", response_model=EmergencyMedicationCard)
def emergency_medication_card(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> EmergencyMedicationCard:
    profile = db.scalar(select(HealthProfile).where(HealthProfile.user_id == current_user.id))
    medications = list(db.scalars(select(Medication).where(Medication.user_id == current_user.id).order_by(Medication.name)))
    substances = list(
        db.scalars(
            select(Substance)
            .where(Substance.user_id == current_user.id, Substance.is_active)
            .order_by(Substance.category, Substance.name)
        )
    )
    safety = run_safety_check_for_user(db, current_user.id)
    high_priority = [
        interaction
        for interaction in safety.interactions
        if interaction.severity in {Severity.high, Severity.critical}
    ]
    log_audit(db, current_user, "generate_emergency_medication_card", "emergency_card", current_user.id)
    db.commit()
    generated_at = datetime.now(timezone.utc)
    return EmergencyMedicationCard(
        full_name=current_user.full_name,
        user_name=current_user.full_name,
        age=profile.age if profile else None,
        allergies=profile.allergies if profile else [],
        conditions=profile.known_conditions if profile else [],
        current_medications=medications,
        substances_lifestyle_risks=substances,
        emergency_contact={
            "name": profile.emergency_contact_name if profile else None,
            "phone": (profile.emergency_contact_phone if profile else None) or current_user.phone_number,
            "email": current_user.email,
        },
        highest_risk_warnings=high_priority,
        generated_at=generated_at,
        generated_date=generated_at,
    )
