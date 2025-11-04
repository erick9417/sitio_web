export type Store = {
  id: string;
  name: string;
};

export type Product = {
  sku: string;
  name: string;
  price: number;
  cost: number;
  stock: number;
  store_id: string;
  store_name: string;
  updated_at: string;
  image_url?: string | null;
};
