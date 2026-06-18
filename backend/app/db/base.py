from app.database import Base

# Import models so SQLAlchemy registers them before create_all.
from app.models import (  # noqa: F401
    AuditLog,
    CaregiverAccess,
    HealthProfile,
    InteractionResult,
    InteractionRule,
    Medication,
    MedicationLog,
    Organization,
    OrganizationMember,
    Reminder,
    Supplement,
    User,
)
