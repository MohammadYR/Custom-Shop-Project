import baseApi from "@/api/base";
import { Category, CategoryQueryFilter, ServerPaginatedResult } from "@/types";

// API functions
export async function getAllCategories(params?: Partial<CategoryQueryFilter>) {
  const res = await baseApi.get<ServerPaginatedResult<Category>>(
    "/admin/categories/",
    { params },
  );
  return res.data;
}

export async function getCategory(id: string) {
  const res = await baseApi.get<Category>(`/admin/categories/${id}/`);
  return res.data;
}

export async function createCategory(data: FormData) {
  const res = await baseApi.post<Category>(`/admin/categories/`, data);
  return res.data;
}

export async function updateCategory(data: FormData) {
  const id = data.get("id");
  const res = await baseApi.put<Category>(`/admin/categories/${id}/`, data);
  return res.data;
}

export async function deleteCategory(id: string | number) {
  const res = await baseApi.delete(`/admin/categories/${id}/`);
  return res.data;
}
