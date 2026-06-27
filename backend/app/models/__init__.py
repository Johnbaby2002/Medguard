from datetime import date, datetime, timezone
from enum import Enum
from uuid import uuid4

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy import Enum as SAEnum
from sqlalchemy import JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


def new_uuid() -> str:
    return str(uuid4())


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class UserRole(str, Enum):
    patient = "patient"
    caregiver = "caregiver"
    clinician = "clinician"
    admin = "admin"


class Sex(str, Enum):
    female = "female"
    male = "male"
    intersex = "intersex"
    other = "other"
    prefer_not_to_say = "prefer_not_to_say"


class MedicationForm(str, Enum):
    tablet = "tablet"
    capsule = "capsule"
    liquid = "liquid"
    injection = "injection"
    inhaler = "inhaler"
    cream = "cream"
    patch = "patch"
    drops = "drops"
    other = "other"


class Severity(str, Enum):
    low = "low"
    moderate = "moderate"
    high = "high"
    critical = "critical"


class InteractionType(str, Enum):
    drug_drug = "drug_drug"
    drug_food = "drug_food"
    drug_supplement = "drug_supplement"
    duplicate_active_ingredient = "duplicate_active_ingredient"
    alcohol = "alcohol"
    grapefruit = "grapefruit"
    caffeine_preworkout = "caffeine_preworkout"
    sedative_combination = "sedative_combination"
    nsaid_duplication = "nsaid_duplication"


class ReminderStatus(str, Enum):
    pending = "pending"
    taken = "taken"
    missed = "missed"


class ScanType(str, Enum):
    barcode = "barcode"
    camera = "camera"
    prescription_ocr = "prescription_ocr"
    upload = "upload"


class ScanStatus(str, Enum):
    draft = "draft"
    matched = "matched"
    needs_review = "needs_review"


class AIReviewStatus(str, Enum):
    pending = "pending"
    completed = "completed"
    failed = "failed"


class IntegrationType(str, Enum):
    wearable = "wearable"
    ehr = "ehr"
    pharmacy = "pharmacy"
    insurance = "insurance"


class IntegrationStatus(str, Enum):
    planned = "planned"
    requested = "requested"
    connected = "connected"
    disabled = "disabled"


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[UserRole] = mapped_column(SAEnum(UserRole), default=UserRole.patient, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)

    health_profile: Mapped["HealthProfile | None"] = relationship(
        back_populates="user", cascade="all, delete-orphan", uselist=False
    )
    medications: Mapped[list["Medication"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    supplements: Mapped[list["Supplement"]] = relationship(back_populates="user", cascade="all, delete-orphan")


class HealthProfile(Base):
    __tablename__ = "health_profiles"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    age: Mapped[int | None] = mapped_column(Integer, nullable=True)
    sex: Mapped[Sex | None] = mapped_column(SAEnum(Sex), nullable=True)
    weight: Mapped[float | None] = mapped_column(nullable=True)
    known_conditions: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    allergies: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    pregnancy_status: Mapped[str | None] = mapped_column(String(100), nullable=True)
    alcohol_use: Mapped[str | None] = mapped_column(String(100), nullable=True)
    caffeine_preworkout_use: Mapped[str | None] = mapped_column(String(100), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)

    user: Mapped[User] = relationship(back_populates="health_profile")


class Medication(Base):
    __tablename__ = "medications"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    active_ingredient: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    dosage: Mapped[str] = mapped_column(String(100), nullable=False)
    form: Mapped[MedicationForm] = mapped_column(SAEnum(MedicationForm), default=MedicationForm.other, nullable=False)
    frequency: Mapped[str] = mapped_column(String(100), nullable=False)
    start_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    end_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    prescribing_doctor: Mapped[str | None] = mapped_column(String(255), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    medication_category: Mapped[str | None] = mapped_column(String(100), index=True, nullable=True)
    is_prescription: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)

    user: Mapped[User] = relationship(back_populates="medications")
    reminders: Mapped[list["Reminder"]] = relationship(back_populates="medication", cascade="all, delete-orphan")
    logs: Mapped[list["MedicationLog"]] = relationship(back_populates="medication", cascade="all, delete-orphan")


class Supplement(Base):
    __tablename__ = "supplements"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    active_ingredient_category: Mapped[str] = mapped_column(String(255), nullable=False)
    dose: Mapped[str] = mapped_column(String(100), nullable=False)
    frequency: Mapped[str] = mapped_column(String(100), nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)

    user: Mapped[User] = relationship(back_populates="supplements")


class InteractionRule(Base):
    __tablename__ = "interaction_rules"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    rule_key: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    severity: Mapped[Severity] = mapped_column(SAEnum(Severity), nullable=False)
    interaction_type: Mapped[InteractionType] = mapped_column(SAEnum(InteractionType), nullable=False)
    terms_a: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    terms_b: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    explanation: Mapped[str] = mapped_column(Text, nullable=False)
    recommendation: Mapped[str] = mapped_column(Text, nullable=False)
    timing_suggestion: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)


class InteractionResult(Base):
    __tablename__ = "interaction_results"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    total_risk_score: Mapped[int] = mapped_column(Integer, nullable=False)
    highest_severity: Mapped[Severity | None] = mapped_column(SAEnum(Severity), nullable=True)
    interactions: Mapped[list[dict]] = mapped_column(JSON, default=list, nullable=False)
    recommended_actions: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    safe_timing_suggestions: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    disclaimer: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)


class Reminder(Base):
    __tablename__ = "reminders"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    medication_id: Mapped[str] = mapped_column(ForeignKey("medications.id", ondelete="CASCADE"), index=True, nullable=False)
    time: Mapped[str] = mapped_column(String(5), nullable=False)
    repeat_pattern: Mapped[str] = mapped_column(String(100), default="daily", nullable=False)
    timezone: Mapped[str] = mapped_column(String(100), default="Europe/Berlin", nullable=False)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)

    medication: Mapped[Medication] = relationship(back_populates="reminders")
    logs: Mapped[list["MedicationLog"]] = relationship(back_populates="reminder")


class MedicationLog(Base):
    __tablename__ = "medication_logs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    medication_id: Mapped[str] = mapped_column(ForeignKey("medications.id", ondelete="CASCADE"), index=True, nullable=False)
    reminder_id: Mapped[str | None] = mapped_column(ForeignKey("reminders.id", ondelete="SET NULL"), nullable=True)
    status: Mapped[ReminderStatus] = mapped_column(SAEnum(ReminderStatus), nullable=False)
    logged_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    medication: Mapped[Medication] = relationship(back_populates="logs")
    reminder: Mapped[Reminder | None] = relationship(back_populates="logs")


class MedicationScan(Base):
    __tablename__ = "medication_scans"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    scan_type: Mapped[ScanType] = mapped_column(SAEnum(ScanType), nullable=False)
    raw_value: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[ScanStatus] = mapped_column(SAEnum(ScanStatus), default=ScanStatus.needs_review, nullable=False)
    confidence: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    medication_draft: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)


class AISafetyReview(Base):
    __tablename__ = "ai_safety_reviews"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    status: Mapped[AIReviewStatus] = mapped_column(SAEnum(AIReviewStatus), default=AIReviewStatus.pending, nullable=False)
    request_source: Mapped[str] = mapped_column(String(100), default="backend", nullable=False)
    input_snapshot: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    ai_result: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    disclaimer: Mapped[str] = mapped_column(
        Text,
        default="This is not medical advice. Consult a doctor or pharmacist.",
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)


class CaregiverAccess(Base):
    __tablename__ = "caregiver_access"
    __table_args__ = (UniqueConstraint("patient_id", "caregiver_id", name="uq_patient_caregiver"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    patient_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    caregiver_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    can_manage: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    missed_dose_alerts: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    relationship: Mapped[str | None] = mapped_column(String(100), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)


class Organization(Base):
    __tablename__ = "organizations"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    organization_type: Mapped[str] = mapped_column(String(100), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)


class OrganizationMember(Base):
    __tablename__ = "organization_members"
    __table_args__ = (UniqueConstraint("organization_id", "user_id", name="uq_org_user"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    organization_id: Mapped[str] = mapped_column(ForeignKey("organizations.id", ondelete="CASCADE"), index=True, nullable=False)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    role: Mapped[UserRole] = mapped_column(SAEnum(UserRole), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)


class IntegrationConnection(Base):
    __tablename__ = "integration_connections"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    user_id: Mapped[str | None] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=True)
    organization_id: Mapped[str | None] = mapped_column(ForeignKey("organizations.id", ondelete="CASCADE"), index=True, nullable=True)
    integration_type: Mapped[IntegrationType] = mapped_column(SAEnum(IntegrationType), nullable=False)
    status: Mapped[IntegrationStatus] = mapped_column(SAEnum(IntegrationStatus), default=IntegrationStatus.planned, nullable=False)
    provider_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    external_reference: Mapped[str | None] = mapped_column(String(255), nullable=True)
    metadata_json: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    actor_user_id: Mapped[str | None] = mapped_column(String(36), index=True, nullable=True)
    action: Mapped[str] = mapped_column(String(100), nullable=False)
    resource_type: Mapped[str] = mapped_column(String(100), nullable=False)
    resource_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    metadata_json: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)


# Compatibility aliases for older demo files that used these names.
DoseStatus = ReminderStatus
DoseLog = MedicationLog
SafetyCheckStatus = ReminderStatus
SafetyCheck = InteractionResult
DoctorReport = InteractionResult
