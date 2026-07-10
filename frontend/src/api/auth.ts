import { api } from "./client";
import type { TokenResponse, UserOut } from "../types/api";

export interface RegisterPayload {
  email: string;
  password: string;
  repeat_password: string;
  full_name: string;
  terms_consent: boolean;
  medical_disclaimer_consent: boolean;
}

export async function register(payload: RegisterPayload) {
  const response = await api.post("/auth/register", payload);
  return response.data;
}
export interface LoginPayload {
  email: string;
  password: string;
}

export async function login(payload: LoginPayload) {
  const response = await api.post<TokenResponse>("/auth/login", payload);
  return response.data;
}

export async function getMe() {
  const response = await api.get<UserOut>("/auth/me");
  return response.data;
}