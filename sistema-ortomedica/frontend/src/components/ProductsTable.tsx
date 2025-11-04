'use client'

import { useState } from 'react'
import { useProducts } from '@/lib/hooks/useProducts'
import { LoadingSpinner } from './LoadingSpinner'
import { Product } from '@/lib/types'
import '@/styles/Catalog.css'

interface ProductsTableProps {
  q?: string
  page: number
  pageSize: number
  onPageChange: (p: number) => void
  onPageSizeChange?: (n: number) => void
  disabled?: boolean
}

function formatCR(date?: string | null) {
  if (!date) return ''
  return new Intl.DateTimeFormat('es-CR', {
    timeZone: 'America/Costa_Rica',
    dateStyle: 'short',
    timeStyle: 'medium',
    hour12: true,
  }).format(new Date(date))
}

function ProductItem({ p }: { p: Product }) {
  const [open, setOpen] = useState(false)
  const hasOffers = p.stores?.length > 0

  return (
    <div className="card">
      <div className="card-head">
        <div className="title-col">
          <div className="title">{p.name}</div>
          <div className="meta">
            <span className="sku">SKU: {p.sku}</span>
          </div>
        </div>
        {hasOffers && (
          <button className="btn-outline" onClick={() => setOpen((v) => !v)}>
            {open ? 'Ocultar bodegas' : 'Ver bodegas'}
          </button>
        )}
      </div>

      {open && hasOffers && (
        <div className="offers">
          <table className="offers-table">
            <thead>
              <tr>
                <th>Bodega</th>
                <th>Precio costo</th>
                <th>Precio venta</th>
                <th>Inventario</th>
                <th>Última actualización</th>
              </tr>
            </thead>
            <tbody>
              {p.stores.map((o, i) => (
                <tr key={i}>
                  <td className="store">{o.name}</td>
                  <td className="price-cost">{(o as any).cost != null ? `₡${((o as any).cost as number).toLocaleString('es-CR')}` : '—'}</td>
                  <td className="price">{o.price != null ? `₡${(o.price as number).toLocaleString('es-CR')}` : '—'}</td>
                  <td className="stock">{o.stock ?? '—'} unidades</td>
                  <td className="when">{(o as any).updated_at ? formatCR((o as any).updated_at) : '—'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}

export function ProductsTable({ q = '', page, pageSize, onPageChange, onPageSizeChange, disabled = false }: ProductsTableProps) {
  const { data, isLoading, isError } = useProducts({ page, pageSize, q })
  const products = data?.items ?? []
  const total = data?.total ?? 0
  const pages = Math.max(1, Math.ceil(total / pageSize))

  if (isLoading) return <div className="hint"><LoadingSpinner /></div>
  if (isError) return <div className="hint text-red-600">Error al cargar los productos.</div>

  return (
    <div className="catalog-main" style={{ opacity: disabled ? 0.6 : 1, pointerEvents: disabled ? 'none' : 'auto' }}>
      <div className="list-controls">
        <label>
          Mostrar:{' '}
          <select
            value={pageSize}
            onChange={(e) => {
              const n = Number((e.currentTarget as HTMLSelectElement).value)
              if (!isNaN(n)) {
                onPageSizeChange?.(n)
                onPageChange(1)
              }
            }}
            className="border rounded px-2 py-1"
            disabled={disabled}
          >
            {[10, 20, 30, 50].map((n) => (
              <option key={n} value={n}>{n}</option>
            ))}
          </select>{' '}productos por página
        </label>
      </div>

      {!isLoading && products.length === 0 && <div className="hint">Sin resultados.</div>}

      <div className="cards">
        {products.map((p) => <ProductItem key={`${p.sku}-${p.name}`} p={p} />)}
      </div>

      <div className="pager">
        <button 
          className="btn small" 
          disabled={page <= 1 || disabled} 
          onClick={() => onPageChange(Math.max(1, page - 1))}
          style={{ minWidth: '100px' }}
        >
          Anterior
        </button>
        <span style={{ margin: '0 15px', lineHeight: '32px' }}>
          Página {page} de {pages}
        </span>
        <button 
          className="btn small" 
          disabled={page >= pages || disabled} 
          onClick={() => onPageChange(Math.min(pages, page + 1))}
          style={{ minWidth: '100px' }}
        >
          Siguiente
        </button>
      </div>
    </div>
  )
}