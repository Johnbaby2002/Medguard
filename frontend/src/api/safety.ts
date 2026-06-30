import { api } from "./client";

export interface SafetyInteraction {
  severity: string;
  interaction_type: string;
  explanation: string;
  recommendation: string;
  disclaimer: string;
  matched_items: string[];
}

export interface SafetyCheckResponse {
  total_risk_score: number;
  highest_severity: string | null;
  interactions: SafetyInteraction[];
  recommended_actions: string[];
  safe_timing_suggestions: string[];
  disclaimer: string;
}

export async function runSafetyCheck() {
  const response = await api.post<SafetyCheckResponse>("/safety-check");
  return response.data;
}