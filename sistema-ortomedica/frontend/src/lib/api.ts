import axios from 'axios'

// Allow overriding the API base via env at build/runtime (Next.js exposes NEXT_PUBLIC_*)
// Fallback to localhost for local development.
const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8001'

const api = axios.create({
  baseURL: API_BASE,
})

export const getProducts = async (opts?: { page?: number; page_size?: number; q?: string }) => {
  const params: Record<string, any> = {}
  if (opts?.page) params.page = opts.page
  if (opts?.page_size) params.page_size = opts.page_size
  if (opts?.q) params.q = opts.q

  const response = await api.get('/products', { params })
  // API returns { items, page, page_size, total }
  const data = response.data ?? {}
  const items = data.items ?? []

  const normalized = (items as any[]).map((it: any) => ({
    id: it.sku ?? `${it.sku}`,
    sku: it.sku,
    name: it.name,
    imageUrl: it.image_url ?? it.imageUrl ?? null,
    // keep both cost and sale price; preserve other fields like updated_at
    stores: (it.offers ?? it.stores ?? []).map((o: any) => ({
      name: o.store_name ?? o.name ?? 'Unknown',
      stock: o.stock ?? o.existencia ?? 0,
      // sale price
      price: o.price ?? o.precio ?? null,
      // cost price (precio costo)
      cost: o.cost ?? o.costo ?? null,
      // timestamp
      updated_at: o.updated_at ?? o.updatedAt ?? null,
    })),
  }))

  return {
    items: normalized,
    page: data.page ?? opts?.page ?? 1,
    page_size: data.page_size ?? opts?.page_size ?? 10,
    total: data.total ?? 0,
  }
}

export const refreshData = async () => {
  // backend exposes ingest runner at POST /ingest/run
  const response = await api.post('/ingest/run')
  return response.data
}

export const getIngestStatus = async () => {
  const response = await api.get('/ingest/status')
  return response.data
}

export const login = async (credentials: { email: string; password: string }) => {
  const response = await api.post('/auth/login', credentials)
  return response.data
}

// Add auth token to all requests if available
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('ortomedica-auth')
  if (token) {
    const auth = JSON.parse(token)
    if (auth.state.token) {
      config.headers.Authorization = `Bearer ${auth.state.token}`
    }
  }
  return config
})