import axios from "axios";

export const api = axios.create({
  baseURL: "/api/v1",
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem("medguard_token");

  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }

  return config;
});