import {
  MutationOptionsFromFn,
  ProductsQueryFilter,
  QueryOptionsFromFn,
} from "@/types";
import {
  createProduct,
  deleteProduct,
  getAllProducts,
  getProduct,
  updateProduct,
} from "./products.api";
import { keepPreviousData, useMutation, useQuery } from "@tanstack/react-query";
import { queryClient } from "../baseQuery";

// All Products
export function useProducts(
  params?: Partial<ProductsQueryFilter>,
  options?: QueryOptionsFromFn<typeof getAllProducts>,
) {
  return useQuery({
    queryKey: ["products", params],
    queryFn: () => getAllProducts(params),
    placeholderData: keepPreviousData,
    ...options,
  });
}

// Create Product
export function useCreateProduct(
  options?: MutationOptionsFromFn<typeof createProduct>,
) {
  const { onSettled, ...rest } = options || {};
  return useMutation({
    mutationFn: createProduct,
    onSettled(data, error, variables, context) {
      queryClient.invalidateQueries({ queryKey: ["products"] });
      onSettled?.(data, error, variables, context);
    },
    ...rest,
  });
}

// Update Product
export function useUpdateProduct(
  id: string | number,
  options?: MutationOptionsFromFn<typeof updateProduct>,
) {
  const { onSettled, ...rest } = options || {};
  return useMutation({
    mutationFn: (data) => updateProduct(data, id),
    onSettled(data, error, variables, context) {
      queryClient.invalidateQueries({ queryKey: ["products"] });
      onSettled?.(data, error, variables, context);
    },
    ...rest,
  });
}

// Delete Product
export function useDeleteProduct(
  options?: MutationOptionsFromFn<typeof deleteProduct>,
) {
  const { onSettled, ...rest } = options || {};
  return useMutation({
    mutationFn: deleteProduct,
    onSettled(data, error, variables, context) {
      queryClient.invalidateQueries({ queryKey: ["products"] });
      onSettled?.(data, error, variables, context);
    },
    ...rest,
  });
}

// Get Single Product
export function useGetProduct(
  id: string,
  options?: QueryOptionsFromFn<typeof getProduct>,
) {
  return useQuery({
    queryKey: ["product", id],
    queryFn: () => getProduct(id),
    enabled: !!id,
    ...options,
  });
}
