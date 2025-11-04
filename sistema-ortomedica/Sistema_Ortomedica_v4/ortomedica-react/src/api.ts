// src/api.ts
/* eslint-disable @typescript-eslint/no-explicit-any */

export type Paged<T> = {
  items: T[];
  page: number;
  page_size: number;
  total: number;
};

export type IngestStatus = {
  busy: boolean;
  status: "idle" | "running" | string;
  started_at?: string | null;
};

const API_BASE = (
  (import.meta as any)?.env?.VITE_API_BASE ||
  "http://127.0.0.1:8000"
).replace(/\/+$/, ""); // sin trailing slash

const TOKEN_KEY = "auth_token";

// ============ Token helpers ============
export function getToken(): string | null {
  try {
    return localStorage.getItem(TOKEN_KEY);
  } catch {
    return null;
  }
}

export function setToken(token: string) {
  try {
    localStorage.setItem(TOKEN_KEY, token);
  } catch {
    // ignore
  }
}

export function clearToken() {
  try {
    localStorage.removeItem(TOKEN_KEY);
  } catch {
    // ignore
  }
}

// ============ URL helper ============
function buildUrl(path: string, params?: Record<string, any>): string {
  const p = path.startsWith("/") ? path : `/${path}`;
  const url = new URL(p, API_BASE);

  if (params) {
    for (const [k, v] of Object.entries(params)) {
      if (v === undefined || v === null || v === "") continue;
      url.searchParams.set(k, String(v));
    }
  }
  return url.toString();
}

// ============ Fetch helpers ============
async function authFetch(
  path: string,
  init: RequestInit = {},
  params?: Record<string, any>
): Promise<Response> {
  const url = buildUrl(path, params);
  const headers = new Headers(init.headers || {});
  headers.set("Accept", "application/json");

  const token = getToken();
  if (token) headers.set("Authorization", `Bearer ${token}`);

  // Si es JSON, setear Content-Type (si no existe)
  if (init.body && !headers.has("Content-Type")) {
    headers.set("Content-Type", "application/json");
  }

  const res = await fetch(url, { ...init, headers });

  if (res.status === 401) {
    // No autorizado: limpiar token para forzar login en UI
    clearToken();
  }
  return res;
}

async function parseJson<T>(res: Response): Promise<T> {
  const text = await res.text();
  try {
    return text ? (JSON.parse(text) as T) : ({} as T);
  } catch {
    // Si no vino JSON, tirar un error amigable
    throw new Error(text || "Respuesta no es JSON");
  }
}

export async function authGet<T = any>(
  path: string,
  params?: Record<string, any>
): Promise<T> {
  const res = await authFetch(path, { method: "GET" }, params);
  if (!res.ok) {
    const msg = await res.text();
    throw new Error(msg || `GET ${path} -> ${res.status}`);
  }
  return parseJson<T>(res);
}

export async function authPost<T = any>(
  path: string,
  body?: any,
  params?: Record<string, any>
): Promise<T> {
  const res = await authFetch(
    path,
    { method: "POST", body: body ? JSON.stringify(body) : undefined },
    params
  );
  if (!res.ok) {
    const msg = await res.text();
    throw new Error(msg || `POST ${path} -> ${res.status}`);
  }
  return parseJson<T>(res);
}

// ============ Auth ============
export type LoginResponse = { access_token: string };

export async function login(email: string, password: string): Promise<string> {
  const res = await fetch(buildUrl("/auth/login"), {
    method: "POST",
    headers: { "Content-Type": "application/json", Accept: "application/json" },
    body: JSON.stringify({ email, password }),
  });

  if (!res.ok) {
    const msg = await res.text();
    throw new Error(msg || "Credenciales inválidas");
  }

  const data = (await res.json()) as LoginResponse;
  if (!data?.access_token) {
    throw new Error("Respuesta de login inválida");
  }
  setToken(data.access_token);
  return data.access_token;
}

// Alias (por si algún archivo anterior lo importaba así)
export const loginApi = login;

export async function logout() {
  clearToken();
}

export async function me(): Promise<any> {
  return authGet("/auth/me");
}

// ============ Ingest ============
export async function startIngest(): Promise<void> {
  // Dispara el proceso de actualización en el backend
  const res = await authFetch("/ingest/run", { method: "POST" });
  if (!res.ok) {
    const msg = await res.text();
    throw new Error(msg || "No se pudo iniciar la actualización");
  }
}

export async function getIngestStatus(): Promise<IngestStatus> {
  const res = await authFetch("/ingest/status", { method: "GET" });
  if (!res.ok) {
    // Algunos backends pueden devolver 422 si no hay estado todavía.
    // Devolvemos un estado por defecto.
    return { busy: false, status: "error", started_at: null };
  }
  return parseJson<IngestStatus>(res);
}

// ============ Helpers genéricos opcionales ============
export async function getPaged<T = any>(
  path: string,
  params?: Record<string, any>
): Promise<Paged<T>> {
  return authGet<Paged<T>>(path, params);
}
