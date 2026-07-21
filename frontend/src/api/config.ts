// src/api/config.ts

export const API_BASE =
  import.meta.env.VITE_API_URL ||
  "https://dataforgecheck.onrender.com";

export const API_PREFIX = `${API_BASE}/api/v1`;