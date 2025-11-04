// src/api.ts
const API = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

async function handle(res: Response) {
  if (res.status === 401) {
    // token inválido/ausente -> limpiamos y a login
    localStorage.removeItem("token");
    if (location.pathname !== "/login") location.href = "/login";
    throw new Error("Unauthorized");
  }
  if (!res.ok) throw new Error(`${res.status}`);
  return res.json();
}

export async function login(email: string, password: string) {
  const res = await fetch(`${API}/auth/login`, {
    method: "POST",
    headers: { "Content-Type":"application/json" },
    body: JSON.stringify({ email, password }),
  });
  return handle(res);
}

export async function authGet<T=any>(path: string, params?: Record<string,string|number|undefined>): Promise<T> {
  const token = localStorage.getItem("token");
  const url = new URL(`${API}${path}`);
  if (params) for (const [k,v] of Object.entries(params)) if (v!==undefined) url.searchParams.set(k, String(v));
  const res = await fetch(url.toString(), {
    headers: token ? { Authorization: `Bearer ${token}` } : {}
  });
  return handle(res);
}

export async function startIngest() {
  const token = localStorage.getItem("token");
  const res = await fetch(`${API}/ingest/run-all`, {
    method: "POST",
    headers: token ? { Authorization: `Bearer ${token}` } : {}
  });
  return handle(res);
}

/** Si decidiste dejar /ingest/status público, no lleva auth.
 *  Si lo dejaste protegido, agrega el header como en authGet. */
export async function getIngestStatus() {
  const res = await fetch(`${API}/ingest/status`);
  return handle(res);
}
