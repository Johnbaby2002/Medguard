import { api } from "./client";
import type { SafetyCheckResponse } from "./safety";

export interface InteractionHistoryItem extends SafetyCheckResponse {
  id: string;
  user_id: string;
  created_at: string;
}

export async function getInteractionHistory() {
  const response = await api.get<InteractionHistoryItem[]>(
    "/interactions/history"
  );

  return response.data;
}