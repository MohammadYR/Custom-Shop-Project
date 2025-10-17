import { CategoryQueryFilter } from "@/types";
import { useQuery } from "@tanstack/react-query";
import { getAllCategories, getCategory } from "./categories.api";

export function useGetCategory(id: string) {
  return useQuery({
    queryKey: ["categories", id],
    queryFn: () => getCategory(id),
    enabled: !!id, // avoids fetching when id is falsy
  });
}
export function useCategories(params?: Partial<CategoryQueryFilter>) {
  return useQuery({
    queryKey: ["categories", params],
    queryFn: () => getAllCategories(params),
  });
}
