import { useQuery } from '@tanstack/react-query'
import { Product } from '../types'
import * as api from '../api'

export function useProducts(opts: { page?: number; pageSize?: number; q?: string }) {
  return useQuery({
    queryKey: ['products', opts.page ?? 1, opts.pageSize ?? 10, opts.q ?? ''],
    queryFn: () => api.getProducts({ page: opts.page, page_size: opts.pageSize, q: opts.q }),
  })
}