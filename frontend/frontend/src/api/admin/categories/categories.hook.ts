import { CategoryQueryFilter, MutationOptionsFromFn } from "@/types";
import {
  createCategory,
  deleteCategory,
  getAllCategories,
  getCategory,
  updateCategory,
} from "./categories.api";
import { useMutation, useQuery } from "@tanstack/react-query";
import { queryClient } from "@/api/baseQuery";

export function useCreateCategory(
  options?: MutationOptionsFromFn<typeof createCategory>,
) {
  return useMutation({
    mutationFn: createCategory,
    onSettled() {
      queryClient.invalidateQueries({ queryKey: ["admin", "categories"] });
    },
    ...options,
  });
}

export function useUpdateCategory(
  options?: MutationOptionsFromFn<typeof updateCategory>,
) {
  return useMutation({
    mutationFn: updateCategory,
    onSettled() {
      queryClient.invalidateQueries({ queryKey: ["admin", "categories"] });
    },
    ...options,
  });
}

export function useDeleteCategory(
  options?: MutationOptionsFromFn<typeof deleteCategory>,
) {
  return useMutation({
    mutationFn: deleteCategory,
    onSettled() {
      queryClient.invalidateQueries({ queryKey: ["admin", "categories"] });
    },
    ...options,
  });
}
export function useGetAminCategory(id: string) {
  return useQuery({
    queryKey: ["admin", "categories", id],
    queryFn: () => getCategory(id),
    enabled: !!id, // avoids fetching when id is falsy
  });
}
export function useAdminCategories(params?: Partial<CategoryQueryFilter>) {
  return useQuery({
    queryKey: ["admin", "categories", params],
    queryFn: () => getAllCategories(params),
  });
}
