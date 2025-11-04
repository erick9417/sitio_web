'use client'

import { useAuth } from '@/lib/auth'
import { usePathname, useRouter } from 'next/navigation'
import { useEffect, useState } from 'react'

export default function AuthGuard({ children }: { children: React.ReactNode }) {
  const { isAuthenticated } = useAuth()
  const router = useRouter()
  const pathname = usePathname()

  // Evita desajustes de hidratación: no renderizar hasta montar en cliente
  const [mounted, setMounted] = useState(false)
  useEffect(() => { setMounted(true) }, [])

  useEffect(() => {
    if (!mounted) return
    // Si no está autenticado y no está en /login, redirige a login
    if (!isAuthenticated() && pathname !== '/login') {
      router.push('/login')
    }
    // Si está autenticado y está en /login, redirige a /products
    else if (isAuthenticated() && pathname === '/login') {
      router.push('/products')
    }
  }, [mounted, isAuthenticated, pathname, router])

  // Hasta que hidrate en cliente, devuelve un placeholder estable
  if (!mounted) return <div />

  // En /login, muestra el contenido sin más
  if (pathname === '/login') {
    return <>{children}</>
  }

  // En otras rutas, muestra el contenido solo si está autenticado
  return isAuthenticated() ? <>{children}</> : null
}