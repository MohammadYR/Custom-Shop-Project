import { Category, CategoryQueryFilter, ServerPaginatedResult } from "@/types";
import baseApi from "../base";

// API functions
export async function getAllCategories(params?: Partial<CategoryQueryFilter>) {
  const res = await baseApi.get<ServerPaginatedResult<Category>>(
    "/categories/",
    { params },
  );
  return res.data;
}

export async function getCategory(id: string) {
  const res = await baseApi.get<Category>(`/categories/${id}/`);
  return res.data;
}
