import Image from "next/image";
import RefreshBar from "../components/RefreshBar"; // si usas alias "@/components/RefreshBar" cámbialo

const API = process.env.NEXT_PUBLIC_API_URL as string;

async function fetchStores() {
  const res = await fetch(`${API}/stores`, { cache: "no-store" });
  return res.json();
}

async function fetchProducts(params: { store_id?: string; q?: string }) {
  const qs = new URLSearchParams();
  if (params.store_id) qs.set("store_id", params.store_id);
  if (params.q) qs.set("q", params.q);
  const res = await fetch(`${API}/products?` + qs.toString(), { cache: "no-store" });
  return res.json();
}

export default async function Home({ searchParams }: { searchParams: { store_id?: string; q?: string } }) {
  const [stores, products] = await Promise.all([
    fetchStores(),
    fetchProducts(searchParams || {}),
  ]);

  return (
    <div>
      {/* Barra de filtros + botón de actualizar */}
      <div className="max-w-6xl mx-auto px-4 py-4 space-y-3">
        <form className="flex items-center gap-3 w-full">
          <input
            name="q"
            defaultValue={searchParams?.q || ""}
            placeholder="Buscar por SKU o nombre…"
            className="border rounded-xl px-3 py-2 w-full max-w-md"
          />
          <select
            name="store_id"
            defaultValue={searchParams?.store_id || ""}
            className="border rounded-xl px-3 py-2"
          >
            <option value="">Todas las bodegas</option>
            {stores.map((s: any) => (
              <option key={s.id} value={s.id}>{s.name}</option>
            ))}
          </select>
          <button className="px-4 py-2 rounded-xl border bg-white hover:bg-gray-100">
            Buscar
          </button>
        </form>

        {/* Botón para disparar scrapers y auto-refresh */}
        <RefreshBar />
      </div>

      {/* Grid de productos */}
      <div className="max-w-6xl mx-auto px-4 pb-10 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        {products.map((p: any) => (
          <div key={`${p.system_id}-${p.store_id}`} className="card p-4">
            <div className="aspect-[4/3] relative mb-3 rounded-xl overflow-hidden">
              <Image
                src={p.image_url || "/placeholder.png"}
                alt={p.name || p.sku || "Producto"}
                fill
                className="object-contain"
              />
            </div>
            <div className="text-sm text-gray-500">{p.sku || "—"}</div>
            <div className="font-semibold leading-tight">{p.name || "Sin nombre"}</div>
            <div className="mt-1 text-sm">Bodega: {p.store_id}</div>

            <div className="mt-3 flex items-center justify-between">
              <span className="text-lg font-bold text-brand-primary">
                ₡{Number(p.precio || 0).toLocaleString("es-CR")}
              </span>
              <span className="text-sm">
                Stock: <strong>{p.existencia ?? 0}</strong>
              </span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
