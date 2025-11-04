'use client'

import { useState, useEffect } from 'react'
import { ProductsTable } from '@/components/ProductsTable'
import { RefreshButton } from '@/components/RefreshButton'
import { useQueryClient, useQuery } from '@tanstack/react-query'
import { getIngestStatus } from '@/lib/api'
import '@/styles/Catalog.css'

export default function ProductsPage() {
  const [mounted, setMounted] = useState(false)
  const [searchTerm, setSearchTerm] = useState('')
  const [page, setPage] = useState(1)
  const [pageSize, setPageSize] = useState(50)

  const qc = useQueryClient()

  // Poll ingest status and trigger refetch when done
  const { data: ingestStatus } = useQuery<any>({
    queryKey: ['ingest', 'status'],
    queryFn: getIngestStatus,
    refetchInterval: (data: any) => {
      // Si está corriendo, chequear cada 3s
      if (data?.busy === true || data?.status === 'running') return 3000
      // Si no está corriendo, chequear cada 10s (por si alguien actualiza desde otra ventana)
      return 10000
    },
  })

  useEffect(() => {
    setMounted(true)
    // Cuando termina (busy=false y status no es 'running'), invalida productos
    if (ingestStatus && !ingestStatus.busy && ingestStatus.status !== 'running') {
      qc.invalidateQueries({ queryKey: ['products'] })
    }
  }, [ingestStatus, qc])

  // Evita desajustes de hidratación iniciales
  if (!mounted) return <div className="catalog-shell" />

  const isUpdating = ingestStatus?.busy === true || ingestStatus?.status === 'running'

  return (
    <div className="catalog-shell">
      <header className="topbar">
        <div className="brand-wrap">
          <img
            src="/logo1.png"
            alt="Ortomédica"
            className="logo"
            onError={(e) => { (e.currentTarget as HTMLImageElement).style.display = 'none' }}
          />
        </div>

        <form className="search" onSubmit={(e) => { e.preventDefault(); }}>
          <input
            placeholder="Buscar productos..."
            value={searchTerm}
            onChange={(e) => { setSearchTerm(e.target.value); setPage(1); }}
            disabled={isUpdating}
            style={{ opacity: isUpdating ? 0.6 : 1, cursor: isUpdating ? 'not-allowed' : 'text' }}
          />
          <button 
            type="submit" 
            className="icon-btn" 
            aria-label="Buscar"
            disabled={isUpdating}
            style={{ opacity: isUpdating ? 0.6 : 1, cursor: isUpdating ? 'not-allowed' : 'pointer' }}
          >
            🔍
          </button>
        </form>

        <div className="toolbar">
          <RefreshButton 
            onStarted={() => qc.invalidateQueries({ queryKey: ['ingest', 'status'] })}
            disabled={isUpdating}
          />
          <div className="ingest-status">
            Estado:{' '}
            {isUpdating ? (
              <span>actualizando...</span>
            ) : ingestStatus?.status === 'error' || ingestStatus?.status === 'failed' ? (
              <span className="err">error</span>
            ) : (
              <span className="ok">listo</span>
            )}
          </div>
        </div>
      </header>

      <ProductsTable
        q={searchTerm}
        page={page}
        pageSize={pageSize}
        onPageChange={(p: number) => setPage(p)}
        onPageSizeChange={(n: number) => { setPageSize(n); setPage(1); }}
        disabled={isUpdating}
      />
    </div>
  )
}