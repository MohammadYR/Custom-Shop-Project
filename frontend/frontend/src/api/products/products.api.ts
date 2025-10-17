import {
  Product,
  ProductDetails,
  ProductsQueryFilter,
  ServerPaginatedResult,
} from "@/types";
import baseApi from "../base";

// API functions
export async function getAllProducts(params?: Partial<ProductsQueryFilter>) {
  const res = await baseApi<ServerPaginatedResult<Product>>("/products", {
    params,
  });
  return res.data;
}

export async function getProduct(id: string) {
  const res = await baseApi<ProductDetails>(`/products/${id}/`);
  return res.data;
}

export async function createProduct(data: FormData) {
  console.log(data);
  const res = await baseApi.post<ProductDetails>("/products/", data);
  return res.data;
}
export async function updateProduct(data: FormData, id: number | string) {
  const res = await baseApi.put<ProductDetails>(`/products/${id}/`, data);
  return res.data;
}
export async function deleteProduct(id: string | number) {
  const res = await baseApi.delete(`/products/${id}/`);
  return res.data;
}
