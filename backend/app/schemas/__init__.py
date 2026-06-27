from datetime import date, datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator, model_validator

from app.models import (
    AIReviewStatus,
    IntegrationStatus,
    IntegrationType,
    InteractionType,
    MedicationForm,
    ReminderStatus,
    ScanStatus,
    ScanType,
    Severity,
    Sex,
    UserRole,
)

MEDICAL_DISCLAIMER = "This is not medical advice. Consult a doctor or pharmacist."


def clean_strings(values: list[str]) -> list[str]:
    return [value.strip() for value in values if value and value.strip()]


def accept_aliases(data: Any, aliases: dict[str, tuple[str, ...]]) -> Any:
    if not isinstance(data, dict):
        return data
    normalized = dict(data)
    for field_name, alias_names in aliases.items():
        if field_name in normalized:
            continue
        for alias in alias_names:
            if alias in normalized:
                normalized[field_name] = normalized[alias]
                break
    return normalized


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=72)
    full_name: str = Field(min_length=1, max_length=255)
    role: UserRole = UserRole.patient

    model_config = ConfigDict(populate_by_name=True, str_strip_whitespace=True)

    @model_validator(mode="before")
    @classmethod
    def accept_frontend_aliases(cls, data: Any) -> Any:
        return accept_aliases(data, {"full_name": ("fullName",)})


class UserLogin(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=72)


class UserOut(BaseModel):
    id: str
    email: EmailStr
    full_name: str
    role: UserRole
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut


class HealthProfileUpsert(BaseModel):
    age: int | None = Field(default=None, ge=0, le=130)
    sex: Sex | None = None
    weight: float | None = Field(default=None, gt=0, le=500)
    known_conditions: list[str] = Field(default_factory=list)
    allergies: list[str] = Field(default_factory=list)
    pregnancy_status: str | None = None
    alcohol_use: str | None = None
    caffeine_preworkout_use: str | None = None

    model_config = ConfigDict(populate_by_name=True, str_strip_whitespace=True)

    @model_validator(mode="before")
    @classmethod
    def accept_frontend_aliases(cls, data: Any) -> Any:
        return accept_aliases(
            data,
            {
                "known_conditions": ("knownConditions",),
                "pregnancy_status": ("pregnancyStatus",),
                "alcohol_use": ("alcoholUse",),
                "caffeine_preworkout_use": ("caffeinePreworkoutUse", "caffeineUse"),
            },
        )

    @field_validator("sex", mode="before")
    @classmethod
    def normalize_sex(cls, value: str | Sex | None) -> str | Sex | None:
        if isinstance(value, str):
            if not value.strip():
                return None
            return value.strip().lower().replace(" ", "_").replace("-", "_")
        return value

    @field_validator("known_conditions", "allergies")
    @classmethod
    def clean_list(cls, value: list[str]) -> list[str]:
        return clean_strings(value)


class HealthProfileOut(HealthProfileUpsert):
    id: str
    user_id: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class MedicationBase(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    active_ingredient: str = Field(default="", max_length=255)
    dosage: str = Field(min_length=1, max_length=100)
    form: MedicationForm = MedicationForm.other
    frequency: str = Field(min_length=1, max_length=100)
    start_date: date | None = None
    end_date: date | None = None
    prescribing_doctor: str | None = None
    notes: str | None = None
    medication_category: str | None = None
    is_prescription: bool = True

    model_config = ConfigDict(populate_by_name=True, str_strip_whitespace=True)

    @model_validator(mode="before")
    @classmethod
    def accept_frontend_aliases(cls, data: Any) -> Any:
        return accept_aliases(
            data,
            {
                "active_ingredient": ("activeIngredient", "ingredient"),
                "start_date": ("startDate",),
                "end_date": ("endDate",),
                "prescribing_doctor": ("prescribingDoctor", "doctor"),
                "medication_category": ("medicationCategory", "category"),
                "is_prescription": ("isPrescription", "prescription"),
            },
        )

    @field_validator("form", mode="before")
    @classmethod
    def normalize_form(cls, value: str | MedicationForm | None) -> str | MedicationForm:
        if value is None or value == "":
            return MedicationForm.other
        if isinstance(value, str):
            return value.strip().lower().replace(" ", "_").replace("-", "_")
        return value

    @model_validator(mode="after")
    def validate_date_range(self) -> "MedicationBase":
        if self.start_date and self.end_date and self.end_date < self.start_date:
            raise ValueError("end_date must be on or after start_date")
        return self


class MedicationCreate(MedicationBase):
    pass


class MedicationUpdate(BaseModel):
    name: str | None = None
    active_ingredient: str | None = None
    dosage: str | None = None
    form: MedicationForm | None = None
    frequency: str | None = None
    start_date: date | None = None
    end_date: date | None = None
    prescribing_doctor: str | None = None
    notes: str | None = None
    medication_category: str | None = None
    is_prescription: bool | None = None

    model_config = ConfigDict(populate_by_name=True, str_strip_whitespace=True)

    @model_validator(mode="before")
    @classmethod
    def accept_frontend_aliases(cls, data: Any) -> Any:
        return accept_aliases(
            data,
            {
                "active_ingredient": ("activeIngredient", "ingredient"),
                "start_date": ("startDate",),
                "end_date": ("endDate",),
                "prescribing_doctor": ("prescribingDoctor", "doctor"),
                "medication_category": ("medicationCategory", "category"),
                "is_prescription": ("isPrescription", "prescription"),
            },
        )

    @field_validator("form", mode="before")
    @classmethod
    def normalize_form(cls, value: str | MedicationForm | None) -> str | MedicationForm | None:
        if value is None or value == "":
            return None
        if isinstance(value, str):
            return value.strip().lower().replace(" ", "_").replace("-", "_")
        return value

    @model_validator(mode="after")
    def validate_date_range(self) -> "MedicationUpdate":
        if self.start_date and self.end_date and self.end_date < self.start_date:
            raise ValueError("end_date must be on or after start_date")
        return self


class MedicationOut(MedicationBase):
    id: str
    user_id: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class SupplementCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    active_ingredient_category: str = Field(min_length=1, max_length=255)
    dose: str = Field(min_length=1, max_length=100)
    frequency: str = Field(min_length=1, max_length=100)
    notes: str | None = None

    model_config = ConfigDict(populate_by_name=True, str_strip_whitespace=True)

    @model_validator(mode="before")
    @classmethod
    def accept_frontend_aliases(cls, data: Any) -> Any:
        return accept_aliases(data, {"active_ingredient_category": ("activeIngredientCategory", "category")})


class SupplementUpdate(BaseModel):
    name: str | None = None
    active_ingredient_category: str | None = None
    dose: str | None = None
    frequency: str | None = None
    notes: str | None = None

    model_config = ConfigDict(populate_by_name=True, str_strip_whitespace=True)

    @model_validator(mode="before")
    @classmethod
    def accept_frontend_aliases(cls, data: Any) -> Any:
        return accept_aliases(data, {"active_ingredient_category": ("activeIngredientCategory", "category")})


class SupplementOut(SupplementCreate):
    id: str
    user_id: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class InteractionRuleCreate(BaseModel):
    rule_key: str
    severity: Severity
    interaction_type: InteractionType
    terms_a: list[str]
    terms_b: list[str] = Field(default_factory=list)
    explanation: str
    recommendation: str
    timing_suggestion: str | None = None
    is_active: bool = True


class InteractionOut(BaseModel):
    severity: Severity
    interaction_type: InteractionType
    explanation: str
    recommendation: str
    disclaimer: str = MEDICAL_DISCLAIMER
    matched_items: list[str] = Field(default_factory=list)


class SafetyCheckResponse(BaseModel):
    total_risk_score: int
    interactions: list[InteractionOut]
    highest_severity: Severity | None = None
    recommended_actions: list[str]
    safe_timing_suggestions: list[str]
    disclaimer: str = MEDICAL_DISCLAIMER


class InteractionHistoryOut(BaseModel):
    id: str
    user_id: str
    total_risk_score: int
    highest_severity: Severity | None = None
    interactions: list[dict[str, Any]]
    recommended_actions: list[str]
    safe_timing_suggestions: list[str]
    disclaimer: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ReminderCreate(BaseModel):
    medication_id: str
    time: str = Field(pattern=r"^\d{2}:\d{2}$")
    repeat_pattern: str = "daily"
    timezone: str = "Europe/Berlin"

    model_config = ConfigDict(populate_by_name=True, str_strip_whitespace=True)

    @model_validator(mode="before")
    @classmethod
    def accept_frontend_aliases(cls, data: Any) -> Any:
        return accept_aliases(data, {"medication_id": ("medicationId",), "repeat_pattern": ("repeatPattern",)})

    @field_validator("time")
    @classmethod
    def validate_time(cls, value: str) -> str:
        hour, minute = (int(part) for part in value.split(":"))
        if hour > 23 or minute > 59:
            raise ValueError("time must be a valid 24-hour HH:MM time")
        return value


class ReminderUpdate(BaseModel):
    time: str | None = Field(default=None, pattern=r"^\d{2}:\d{2}$")
    repeat_pattern: str | None = None
    timezone: str | None = None
    enabled: bool | None = None

    model_config = ConfigDict(populate_by_name=True, str_strip_whitespace=True)

    @model_validator(mode="before")
    @classmethod
    def accept_frontend_aliases(cls, data: Any) -> Any:
        return accept_aliases(data, {"repeat_pattern": ("repeatPattern",)})

    @field_validator("time")
    @classmethod
    def validate_time(cls, value: str | None) -> str | None:
        if value is None:
            return None
        hour, minute = (int(part) for part in value.split(":"))
        if hour > 23 or minute > 59:
            raise ValueError("time must be a valid 24-hour HH:MM time")
        return value


class ReminderOut(BaseModel):
    id: str
    user_id: str
    medication_id: str
    medication_name: str | None = None
    time: str
    repeat_pattern: str
    timezone: str
    enabled: bool
    taken_status: bool = False
    missed_status: bool = False
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class MedicationLogOut(BaseModel):
    id: str
    user_id: str
    medication_id: str
    reminder_id: str | None = None
    status: ReminderStatus
    logged_at: datetime
    notes: str | None = None

    model_config = ConfigDict(from_attributes=True)


class MedicationHistoryResponse(BaseModel):
    logs: list[MedicationLogOut]
    adherence_summary: dict[str, Any]


class MedicationSummaryReport(BaseModel):
    user_profile_summary: dict[str, Any]
    current_medications: list[MedicationOut]
    supplements: list[SupplementOut]
    detected_risks: SafetyCheckResponse
    adherence_summary: dict[str, Any]
    missed_doses: list[MedicationLogOut]
    doctor_pharmacist_notes: list[str]
    disclaimer: str = MEDICAL_DISCLAIMER


class BarcodeScanRequest(BaseModel):
    barcode: str = Field(min_length=3, max_length=100)
    product_name: str | None = None
    active_ingredient: str | None = None
    dosage: str | None = None
    notes: str | None = None

    model_config = ConfigDict(str_strip_whitespace=True)

    @model_validator(mode="before")
    @classmethod
    def accept_frontend_aliases(cls, data: Any) -> Any:
        return accept_aliases(data, {"product_name": ("productName",), "active_ingredient": ("activeIngredient",)})


class PrescriptionOCRDraftRequest(BaseModel):
    ocr_text: str = Field(min_length=1)
    image_reference: str | None = None

    model_config = ConfigDict(str_strip_whitespace=True)

    @model_validator(mode="before")
    @classmethod
    def accept_frontend_aliases(cls, data: Any) -> Any:
        return accept_aliases(data, {"ocr_text": ("ocrText",), "image_reference": ("imageReference",)})


class MedicationDraftOut(BaseModel):
    name: str
    active_ingredient: str
    dosage: str
    form: MedicationForm = MedicationForm.other
    frequency: str = "confirm with label"
    medication_category: str | None = None
    is_prescription: bool = True
    notes: str | None = None


class MedicationScanOut(BaseModel):
    id: str
    user_id: str
    scan_type: ScanType
    raw_value: str
    status: ScanStatus
    confidence: int
    medication_draft: dict[str, Any]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AISafetyReviewCreate(BaseModel):
    request_source: str = "backend"


class AISafetyReviewResultUpdate(BaseModel):
    status: AIReviewStatus = AIReviewStatus.completed
    ai_result: dict[str, Any] | None = None
    error_message: str | None = None

    model_config = ConfigDict(populate_by_name=True, str_strip_whitespace=True)

    @model_validator(mode="before")
    @classmethod
    def accept_frontend_aliases(cls, data: Any) -> Any:
        return accept_aliases(data, {"ai_result": ("aiResult",), "error_message": ("errorMessage",)})


class AISafetyReviewOut(BaseModel):
    id: str
    user_id: str
    status: AIReviewStatus
    request_source: str
    input_snapshot: dict[str, Any]
    ai_result: dict[str, Any] | None = None
    error_message: str | None = None
    disclaimer: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class EmergencyMedicationCard(BaseModel):
    patient: dict[str, Any]
    allergies: list[str]
    known_conditions: list[str]
    current_medications: list[MedicationOut]
    supplements: list[SupplementOut]
    high_priority_warnings: list[InteractionOut]
    generated_at: datetime
    disclaimer: str = MEDICAL_DISCLAIMER


class IntegrationConnectionCreate(BaseModel):
    integration_type: IntegrationType
    provider_name: str | None = None
    external_reference: str | None = None
    metadata_json: dict[str, Any] = Field(default_factory=dict)
    organization_id: str | None = None
    status: IntegrationStatus = IntegrationStatus.requested

    model_config = ConfigDict(populate_by_name=True, str_strip_whitespace=True)

    @model_validator(mode="before")
    @classmethod
    def accept_frontend_aliases(cls, data: Any) -> Any:
        return accept_aliases(
            data,
            {
                "integration_type": ("integrationType",),
                "provider_name": ("providerName",),
                "external_reference": ("externalReference",),
                "metadata_json": ("metadata", "metadataJson"),
                "organization_id": ("organizationId",),
            },
        )


class IntegrationConnectionOut(BaseModel):
    id: str
    user_id: str | None = None
    organization_id: str | None = None
    integration_type: IntegrationType
    status: IntegrationStatus
    provider_name: str | None = None
    external_reference: str | None = None
    metadata_json: dict[str, Any]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class SupportedLanguageOut(BaseModel):
    code: str
    name: str
    status: str


class CaregiverInvite(BaseModel):
    caregiver_email: EmailStr
    relationship: str | None = None
    can_manage: bool = False
    missed_dose_alerts: bool = True

    model_config = ConfigDict(populate_by_name=True, str_strip_whitespace=True)

    @model_validator(mode="before")
    @classmethod
    def accept_frontend_aliases(cls, data: Any) -> Any:
        return accept_aliases(
            data,
            {
                "caregiver_email": ("caregiverEmail",),
                "can_manage": ("canManage",),
                "missed_dose_alerts": ("missedDoseAlerts",),
            },
        )


class CaregiverAccessOut(BaseModel):
    id: str
    patient_id: str
    caregiver_id: str
    relationship: str | None = None
    can_manage: bool
    missed_dose_alerts: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class OrganizationCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    organization_type: str = Field(min_length=1, max_length=100)


class OrganizationOut(OrganizationCreate):
    id: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class OrganizationMemberCreate(BaseModel):
    user_email: EmailStr
    role: UserRole


class OrganizationMemberOut(BaseModel):
    id: str
    organization_id: str
    user_id: str
    role: UserRole
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
