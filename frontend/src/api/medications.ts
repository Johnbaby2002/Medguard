import { api } from "./client";

export interface Medication {
  id: string;
  name: string;
  dosage: string;
  frequency: string;
  medication_type: string;
  is_active: boolean;
  created_at?: string;
  updated_at?: string;
}

export interface CreateMedicationPayload {
  name: string;
  dosage: string;
  frequency: string;
  medication_type: string;
}

export async function getMedications() {
  const response = await api.get<Medication[]>("/medications");
  return response.data;
}

export async function createMedication(payload: CreateMedicationPayload) {
  const response = await api.post<Medication>("/medications", payload);
  return response.data;
}

export async function deleteMedication(id: string) {
  await api.delete(`/medications/${id}`);
}