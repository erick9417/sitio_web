import React, { useState } from "react";
import "./product-card.css";

export type StoreRow = {
  store_name: string;
  product_name: string;
  sku: string;
  costo: number | null;
  precio: number | null;
  existencia: number | null;
  last_update: string | null;
};

export type Product = {
  sku: string;
  name: string;
  brand?: string | null;
  description?: string | null;
  image_url?: string | null;
  stores: StoreRow[]; // Todas las bodegas de ese SKU
};

function currency(n: number | null | undefined) {
  if (n == null) return "—";
  return new Intl.NumberFormat("es-CR", {
    style: "currency",
    currency: "CRC",
    maximumFractionDigits: 0,
  }).format(n);
}

export default function ProductCard({ p }: { p: Product }) {
  const [open, setOpen] = useState(true); // desplegado por defecto
  return (
    <article className="pc">
      <div className="pc__head" onClick={() => setOpen((v) => !v)}>
        <img
          className="pc__img"
          src={p.image_url || "/placeholder.png"}
          onError={(e) => {
            (e.target as HTMLImageElement).src = "/placeholder.png";
          }}
          alt={p.name}
        />
        <div className="pc__meta">
          <div className="pc__title-row">
            <h3 className="pc__title">{p.name}</h3>
            <span className="pc__sku">SKU: {p.sku}</span>
          </div>
          {p.brand ? <div className="pc__brand">{p.brand}</div> : null}
          {p.description ? (
            <p className="pc__desc">{p.description}</p>
          ) : null}
        </div>
        <button
          className="pc__toggle"
          aria-label={open ? "Ocultar bodegas" : "Mostrar bodegas"}
        >
          {open ? "Ocultar bodegas" : "Ver bodegas"}
        </button>
      </div>

      {open && (
        <div className="pc__body">
          <table className="pc__tbl">
            <thead>
              <tr>
                <th style={{ width: "22%" }}>Bodega</th>
                <th>Producto</th>
                <th style={{ width: "12%" }}>Costo</th>
                <th style={{ width: "12%" }}>Precio</th>
                <th style={{ width: "12%" }}>Inventario</th>
                <th style={{ width: "16%" }}>Última actualización</th>
              </tr>
            </thead>
            <tbody>
              {p.stores.map((s, i) => (
                <tr key={p.sku + i}>
                  <td>{s.store_name}</td>
                  <td className="pc__prod-name">{s.product_name}</td>
                  <td>{currency(s.costo)}</td>
                  <td><b className="pc__price">{currency(s.precio)}</b></td>
                  <td className="pc__inv">{s.existencia ?? "—"}</td>
                  <td className="pc__date">
                    {s.last_update ? (
                      <span className="pc__date--ok">{s.last_update}</span>
                    ) : (
                      "—"
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </article>
  );
}
