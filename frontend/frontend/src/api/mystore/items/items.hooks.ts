import {
  getMyStoreItems,
  getMyStoreItem,
  addMyStoreItems,
  update,
  deleteMyStoreItems,
} from "./items.api";
import {
  MutationOptionsFromFn,
  QueryOptionsFromFn,
  StoreItemQueryFilter,
} from "@/types";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";

// Fetch all items
export function useMyStoreItems(
  params?: Partial<StoreItemQueryFilter>,
  options?: QueryOptionsFromFn<typeof getMyStoreItems>,
) {
  return useQuery({
    queryKey: ["my-store-items", params],
    queryFn: () => getMyStoreItems(params),
    ...options,
  });
}

// Fetch single item
export function useMyStoreItem(
  id: string | number,
  options?: QueryOptionsFromFn<typeof getMyStoreItem>,
) {
  return useQuery({
    queryKey: ["my-store-item", id],
    queryFn: () => getMyStoreItem(id),
    enabled: !!id,
    ...options,
  });
}

// Create item
export function useAddMyStoreItem(
  options?: MutationOptionsFromFn<typeof addMyStoreItems>,
) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: addMyStoreItems,
    onSuccess: (...args) => {
      queryClient.invalidateQueries({ queryKey: ["my-store-items"] });
      options?.onSuccess?.(...args);
    },
    ...options,
  });
}

// Update item
export function useUpdateMyStoreItem(
  options?: MutationOptionsFromFn<typeof update>,
) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: update,
    onSuccess: (...args) => {
      queryClient.invalidateQueries({ queryKey: ["my-store-items"] });
      options?.onSuccess?.(...args);
    },
    ...options,
  });
}

// Delete item
export function useDeleteMyStoreItem(
  options?: MutationOptionsFromFn<typeof deleteMyStoreItems>,
) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: deleteMyStoreItems,
    onSuccess: (...args) => {
      queryClient.invalidateQueries({ queryKey: ["my-store-items"] });
      options?.onSuccess?.(...args);
    },
    ...options,
  });
}
