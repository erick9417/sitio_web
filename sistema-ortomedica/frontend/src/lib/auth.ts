import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import * as api from './api'

interface AuthState {
  token: string | null
  user: any | null
  setAuth: (token: string, user: any) => void
  clearAuth: () => void
  isAuthenticated: () => boolean
}

export const useAuth = create<AuthState>()(
  persist(
    (set: any, get: any) => ({
      token: null,
      user: null,
      setAuth: (token, user) => set({ token, user }),
      clearAuth: () => set({ token: null, user: null }),
      isAuthenticated: () => !!get().token,
    }),
    {
      name: 'ortomedica-auth',
    }
  )
)

export async function login(email: string, password: string) {
  const response = await api.login({ email, password })
  if (response.access_token) {
    useAuth.getState().setAuth(response.access_token, null)
    return true
  }
  return false
}

export function logout() {
  useAuth.getState().clearAuth()
}