// src/pages/Catalog.tsx
import React from "react";
import { authGet, getIngestStatus, startIngest } from "../api";

/* ========================= Tipos ========================= */
type Offer = {
  store_id: number;
  store_name?: string | null;
  price: number | null;
  cost: number | null;
  stock: number | null;
  updated_at: string | null;
};

type Product = {
  sku: string;
  name: string;
  brand?: string | null;
  description?: string | null;
  offers: Offer[];
};

type Paged<T> = {
  items: T[];
  page: number;
  page_size: number;
  total: number;
};

/* ========================= Utiles ========================= */
function formatCR(iso?: string | null) {
  if (!iso) return "";
  return new Intl.DateTimeFormat("es-CR", {
    timeZone: "America/Costa_Rica",
    dateStyle: "short",
    timeStyle: "medium",
    hour12: true,
  }).format(new Date(iso));
}

/* ============ Hook: estado de ingest/polling ============== */
function useIngestStatus(pollMs = 60000) {
  const [busy, setBusy] = React.useState(false);
  const [status, setStatus] = React.useState<"idle" | "running" | string>("idle");
  const [last, setLast] = React.useState<string | null>(null);

  const refresh = React.useCallback(async () => {
    try {
      const s = await getIngestStatus(); // {busy,status,last_success_at,...}
      setBusy(!!s.busy);
      setStatus((s.status as any) || "idle");
      setLast(s.last_success_at ?? null);
    } catch {
      // silencio
    }
  }, []);

  React.useEffect(() => {
    refresh();
    const t = setInterval(refresh, pollMs);
    return () => clearInterval(t);
  }, [refresh, pollMs]);

  return { busy, status, last, refresh };
}

/* ================== Item de producto ====================== */
function ProductItem({ p }: { p: Product }) {
  const [open, setOpen] = React.useState(false);
  const hasOffers = p.offers?.length > 0;

  return (
    <div className="card">
      <div className="card-head">
        <div className="title-col">
          <div className="title">{p.name}</div>
          <div className="meta">
            {p.brand ? <span className="brand">{p.brand}</span> : null}
            <span className="sku">SKU: {p.sku}</span>
          </div>
        </div>
        {hasOffers && (
          <button className="btn-outline" onClick={() => setOpen((v) => !v)}>
            {open ? "Ocultar bodegas" : "Ver bodegas"}
          </button>
        )}
      </div>

      {open && hasOffers && (
        <div className="offers">
          <table className="offers-table">
            <thead>
              <tr>
                <th>Bodega</th>
                <th>Costo</th>
                <th>Precio</th>
                <th>Inventario</th>
                <th>Última actualización</th>
              </tr>
            </thead>
            <tbody>
              {p.offers.map((o, i) => (
                <tr key={i}>
                  <td className="store">
                    {o.store_name?.trim() ? o.store_name : `Bodega #${o.store_id}`}
                  </td>
                  <td>{o.cost != null ? `₡${o.cost.toLocaleString("es-CR")}` : "—"}</td>
                  <td className="price">
                    {o.price != null ? `₡${o.price.toLocaleString("es-CR")}` : "—"}
                  </td>
                  <td className="stock">{o.stock ?? "—"}</td>
                  <td className="when">{o.updated_at ? formatCR(o.updated_at) : "—"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

/* ====================== Página ============================ */
export default function CatalogPage() {
  // UI
  const [q, setQ] = React.useState("");
  const [page, setPage] = React.useState(1);
  const [pageSize, setPageSize] = React.useState(50); // 50 por defecto

  // Datos
  const [rows, setRows] = React.useState<Product[]>([]);
  const [total, setTotal] = React.useState(0);
  const [loading, setLoading] = React.useState(false);

  // Ingest status
  const { busy, status, last, refresh: refreshIngest } = useIngestStatus(60000);

  const pages = Math.max(1, Math.ceil(total / pageSize));

  const fetchPage = React.useCallback(
    async (p: number, sz: number, query: string) => {
      setLoading(true);
      try {
        const params: Record<string, string | number | undefined> = {
          page: p,
          page_size: sz,
          q: query?.trim() || undefined,
        };
        const resp: Paged<Product> = await authGet("/products", params);
        setRows(resp.items || []);
        setTotal(resp.total || 0);
      } catch (e) {
        console.error(e);
        setRows([]);
        setTotal(0);
      } finally {
        setLoading(false);
      }
    },
    []
  );

  React.useEffect(() => {
    fetchPage(page, pageSize, q);
  }, [page, pageSize, q, fetchPage]);

  const onSearch = (ev: React.FormEvent) => {
    ev.preventDefault();
    setPage(1); // el efecto recarga
  };

  const onStartIngest = async () => {
    try {
      // bloquea el botón mostrando "Actualizando..."
      await startIngest();
      // hacemos un pequeño ciclo de polling más rápido hasta que deje de estar "running"
      const pollFast = async () => {
        for (let i = 0; i < 60; i++) {
          await new Promise((r) => setTimeout(r, 2000));
          await refreshIngest();
          const s = await getIngestStatus();
          if (!s.busy && s.status !== "running") break;
        }
      };
      await pollFast();
      await refreshIngest(); // refrescar estado final (y last_success_at)
      // recargar página actual
      fetchPage(page, pageSize, q);
      alert("Actualización terminada.");
    } catch (e: any) {
      console.error(e);
      alert(e?.message || "No se pudo iniciar la actualización.");
    }
  };

  return (
    <div className="catalog-shell">

      <header className="topbar">
        <div className="brand-wrap">
          <img
            src="/logo1.png"
            alt="Ortomédica"
            className="logo"
            onError={(e) => {
              // si no hay logo.svg, muestra texto
              (e.currentTarget as HTMLImageElement).style.display = "none";
            }}
          />
        </div>

        <form className="search" onSubmit={onSearch}>
          <input
            placeholder="Buscar productos..."
            value={q}
            onChange={(e) => setQ(e.target.value)}
          />
          <button type="submit" className="icon-btn" aria-label="Buscar">🔍</button>
        </form>

        <div className="toolbar">
          <button
            className="btn primary"
            onClick={onStartIngest}
            disabled={busy}
            title="Forzar actualización ahora"
          >
            {busy ? "Actualizando..." : "Actualizar"}
          </button>
          <div className="ingest-status">
            Estado: <b>{busy ? "ocupado" : (status || "idle")}</b>
            {last ? <> · Última: {formatCR(last)}</> : null}
          </div>
        </div>
      </header>

      <main className="catalog-main">
        <div className="list-controls">
          <label>
            Mostrar:{" "}
            <select
              value={pageSize}
              onChange={(e) => {
                setPageSize(parseInt(e.target.value, 10));
                setPage(1);
              }}
            >
              {[10, 20, 30, 50].map((n) => (
                <option key={n} value={n}>
                  {n}
                </option>
              ))}
            </select>{" "}
            productos por página
          </label>

          <div className="pager">
            <button
              className="btn small"
              disabled={page <= 1 || loading}
              onClick={() => setPage((p) => Math.max(1, p - 1))}
            >
              Anterior
            </button>
            <button
              className="btn small"
              disabled={page >= pages || loading}
              onClick={() => setPage((p) => Math.min(pages, p + 1))}
            >
              Siguiente
            </button>
          </div>
        </div>

        {loading && <div className="hint">Cargando…</div>}
        {!loading && rows.length === 0 && <div className="hint">Sin resultados.</div>}

        <div className="cards">
          {rows.map((p) => (
            <ProductItem key={`${p.sku}-${p.name}`} p={p} />
          ))}
        </div>
      </main>

      {/* ======= Estilos mínimos ======= */}
      <style>{`
        .catalog-shell { display:flex; flex-direction:column; min-height:100vh; background:#f6f7fb; color:#1f2937; }
        .topbar {
          display:flex; align-items:center; gap:16px; justify-content:space-between;
          padding:12px 16px; background:#0f4fa8; color:#fff; position:sticky; top:0; z-index:5;
        }
        .brand-wrap { display:flex; align-items:center; gap:10px; }
        .brand-text { font-weight:600; opacity:.95; }
        .logo { height:45px; }

        .search { display:flex; align-items:center; gap:6px; flex:1; max-width:560px; margin:0 12px; }
        .search input {
          width:100%; height:36px; border-radius:8px; border:1px solid #d1d5db; padding:0 10px; outline:none;
          background:#fff; color:#111; /* texto visible */
        }
        .icon-btn { height:36px; border-radius:8px; padding:0 10px; border:1px solid #d1d5db; background:#fff; cursor:pointer; }

        .toolbar { display:flex; align-items:center; gap:12px; }
        .btn { height:36px; padding:0 14px; border-radius:8px; border:1px solid #cbd5e1; background:#fff; cursor:pointer; }
        .btn.primary { background:#2563eb; border-color:#2563eb; color:#fff; }
        .btn:disabled { opacity:.6; cursor:not-allowed; }
        .btn.small { height:32px; padding:0 10px; }
        .ingest-status { font-size:.9rem; opacity:.95; }

        .catalog-main { width:100%; max-width:1024px; margin:24px auto; padding:0 16px; }
        .list-controls { display:flex; align-items:center; justify-content:space-between; margin-bottom:12px; }
        .pager { display:flex; gap:8px; }

        .cards { display:flex; flex-direction:column; gap:12px; }
        .card { background:#fff; border:1px solid #e5e7eb; border-radius:12px; box-shadow:0 1px 2px rgba(0,0,0,.04); }
        .card-head {
          display:flex; align-items:flex-start; justify-content:space-between; gap:12px;
          padding:14px 16px 10px 16px; border-bottom:1px solid #f1f5f9;
        }
        .title-col { min-width:0; }
        .title { font-weight:600; font-size:1.05rem; line-height:1.35; }
        .meta { margin-top:4px; display:flex; gap:10px; font-size:.9rem; color:#6b7280; }
        .brand { padding-right:10px; border-right:1px solid #e5e7eb; }
        .sku { padding-left:4px; }

        .btn-outline {
          border:1px solid #cbd5e1; background:#fff; color:#0f172a; height:32px; padding:0 10px;
          border-radius:8px; cursor:pointer;
        }

        .offers { padding:8px 16px 14px 16px; }
        .offers-table { width:100%; border-collapse:collapse; }
        .offers-table th, .offers-table td {
          text-align:left; padding:10px 8px; border-bottom:1px solid #f1f5f9; font-size:.95rem;
        }
        .offers-table th { color:#6b7280; font-weight:600; }
        .offers-table td.price { color:#b45309; font-weight:600; }
        .offers-table td.stock { font-weight:600; }
        .offers-table td.when { color:#ef4444; font-weight:600; }
        .store { font-weight:600; color:#111827; }
        .hint { margin:24px 0; text-align:center; color:#6b7280; }
      `}</style>
    </div>
  );
}
