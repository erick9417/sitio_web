export interface Product {
  id: string | number
  sku: string
  name: string
  stores: Store[]
  imageUrl?: string
}

export interface Store {
  name: string
  stock: number
  price: number | null
  cost?: number | null
  updated_at?: string
}