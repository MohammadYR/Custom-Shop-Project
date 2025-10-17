import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { PaginateQuery, ServerPaginatedResult, ShopOrder } from "@/types";
import { ordersApi } from "./api";

export const useStoreOrders = (params: Partial<PaginateQuery>) => {
  return useQuery<ServerPaginatedResult<ShopOrder>>({
    queryKey: ["store-orders", params],
    queryFn: () => ordersApi.getAll(params),
  });
};

export const useStoreOrder = (id: string | number) => {
  return useQuery<ShopOrder>({
    queryKey: ["store-order", id],
    queryFn: () => ordersApi.getOne(id),
    enabled: !!id,
  });
};

export const useChangeOrderStatus = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ordersApi.changeStatus,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["store-orders"] });
    },
  });
};
