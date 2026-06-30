import { api } from "./client";
import type { TokenResponse, UserOut } from "../types/api";

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