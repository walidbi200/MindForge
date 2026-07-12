// VITE_* variables are inlined at build time by Vite.
// A Vercel env-var change requires a new deployment, not just a restart.
export const API_BASE_URL =
  import.meta.env.VITE_API_URL ?? "http://localhost:8000";

// Shared secret sent with every AI request. Set VITE_APP_KEY on Vercel.
// Empty string means no protection (safe for local dev without env vars).
export const APP_KEY: string = import.meta.env.VITE_APP_KEY ?? "";
