import { useEffect, useState } from "react";

type Props = {
  apiBase: string; // ej: http://127.0.0.1:8000
};

export default function RefreshBar({ apiBase }: Props) {
  const [busy, setBusy] = useState(false);
  const token = localStorage.getItem("token") ?? "";

  async function poll() {
    try {
      const r = await fetch(`${apiBase}/ingest/status`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      const j = await r.json();
      setBusy(Boolean(j?.busy));
    } catch {
      // silenciar (si la API no responde, evitamos romper el UI)
    }
  }

  useEffect(() => {
    poll();
    const id = window.setInterval(poll, 5000);
    return () => clearInterval(id);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [apiBase, token]);

  async function startIngest() {
    try {
      const res = await fetch(`${apiBase}/ingest/run-all`, {
        method: "POST",
        headers: { Authorization: `Bearer ${token}` },
      });
      if (!res.ok) {
        alert(`No se pudo iniciar la actualización: /ingest/run-all: ${res.status}`);
        return;
      }
      alert("Ingest iniciado correctamente ✅");
      poll();
    } catch (e) {
      alert("Error iniciando ingest");
      console.error(e);
    }
  }

  return (
    <div className="flex items-center gap-3">
      <button
        onClick={startIngest}
        disabled={busy}
        className="px-3 py-2 rounded bg-blue-600 text-white hover:bg-blue-700 disabled:opacity-60"
      >
        {busy ? "Actualizando…" : "Actualizar inventario"}
      </button>
      <span className="text-sm text-gray-600">
        Auto-refresco cada 5s · Estado: <b>{busy ? "ocupado" : "idle"}</b>
      </span>
    </div>
  );
}
