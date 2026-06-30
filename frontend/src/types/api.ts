export type UserRole = "patient" | "caregiver" | "clinician" | "admin";
export type Sex = "male" | "female" | "other" | "prefer_not_to_say";
export type MedicationForm =
  | "tablet"
  | "capsule"
  | "liquid"
  | "injection"
  | "cream"
  | "inhaler"
  | "drops"
  | "patch"
  | "other";

export type Severity = "low" | "moderate" | "high" | "critical";
export type InteractionType =
  | "drug_drug"
  | "drug_supplement"
  | "drug_condition"
  | "duplicate_therapy"
  | "food_interaction"
  | "lifestyle_interaction";

export interface UserOut {
  id: string;
  email: string;
  full_name: string;
  role: UserRole;
  created_at: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: "bearer";
  user: UserOut;
}

export interface MedicationOut {
  id: string;
  user_id: string;
  name: string;
  active_ingredient: string;
  dosage: string;
  form: MedicationForm;
  frequency: string;
  start_date: string | null;
  end_date: string | null;
  prescribing_doctor: string | null;
  notes: string | null;
  medication_category: string | null;
  is_prescription: boolean;
  created_at: string;
  updated_at: string;
}

export interface ReminderOut {
  id: string;
  user_id: string;
  medication_id: string;
  medication_name: string | null;
  time: string;
  repeat_pattern: string;
  timezone: string;
  enabled: boolean;
  taken_status: boolean;
  missed_status: boolean;
  created_at: string;
}

export interface InteractionOut {
  severity: Severity;
  interaction_type: InteractionType;
  explanation: string;
  recommendation: string;
  disclaimer: string;
  matched_items: string[];
}

export interface SafetyCheckResponse {
  total_risk_score: number;
  interactions: InteractionOut[];
  highest_severity: Severity | null;
  recommended_actions: string[];
  safe_timing_suggestions: string[];
  disclaimer: string;
}

export interface DashboardSummary {
  active_medications: number;
  supplements: number;
  active_reminders: number;
  taken_doses: number;
  missed_doses: number;
  latest_total_risk_score: number;
  latest_highest_severity: Severity | null;
}