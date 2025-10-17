import { Order, ServerPaginatedResult } from "@/types";
import {
  useMutation,
  UseMutationOptions,
  useQuery,
  UseQueryOptions,
} from "@tanstack/react-query";
import {
  CreateOrderPayload,
  CreateOrderResponse,
  createUserOrder,
  getUserOrder,
  getUserOrders,
} from "./orders.api";

const ORDERS_QUERY_KEY = "orders";
export function useOrdersQuery(
  params?: Record<string, string | number | undefined>,
  options?: UseQueryOptions<ServerPaginatedResult<Order>, Error>,
) {
  return useQuery({
    queryKey: [ORDERS_QUERY_KEY, params],
    queryFn: () => getUserOrders(params),
    ...options,
  });
}

export function useOrderQuery(
  id: string,
  options?: UseQueryOptions<Order, Error>,
) {
  return useQuery({
    queryKey: [ORDERS_QUERY_KEY, id],
    queryFn: () => getUserOrder(id),
    ...options,
  });
}

export function useOrderMutation(
  options?: UseMutationOptions<CreateOrderResponse, Error, CreateOrderPayload>,
) {
  return useMutation({
    mutationFn: (data: CreateOrderPayload) => createUserOrder(data),
    ...options,
  });
}
