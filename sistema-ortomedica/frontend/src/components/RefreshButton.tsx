'use client'

import * as api from '@/lib/api'
import { useState } from 'react'
import { useQueryClient } from '@tanstack/react-query'

export function RefreshButton({ onStarted, disabled }: { onStarted?: () => void; disabled?: boolean } = {}) {
  const [running, setRunning] = useState(false)
  const qc = useQueryClient()

  const handleRefresh = async () => {
    if (running || disabled) return
    try {
      setRunning(true)
      onStarted?.()
      await api.refreshData()
      // ensure ingest status is refetched right away
      qc.invalidateQueries({ queryKey: ['ingest', 'status'] })
    } catch (error) {
      console.error('Error al actualizar:', error)
    } finally {
      setRunning(false)
    }
  }

  const isDisabled = running || disabled

  return (
    <button
      onClick={handleRefresh}
      disabled={isDisabled}
      className="btn primary"
      style={{
        backgroundColor: '#0f4fa8',
        borderColor: '#0f4fa8',
        color: '#fff',
        fontSize: '0.95rem',
        transition: 'all 0.2s',
        opacity: isDisabled ? 0.6 : 1,
        cursor: isDisabled ? 'not-allowed' : 'pointer'
      }}
    >
      {disabled ? 'Actualizando...' : running ? 'Iniciando...' : 'Actualizar Datos'}
    </button>
  )
}