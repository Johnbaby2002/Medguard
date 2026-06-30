import { api } from "./client";
import type { DashboardSummary } from "../types/api";

export async function getDashboardSummary() {
  const response = await api.get<DashboardSummary>("/dashboard");
  return response.data;
}