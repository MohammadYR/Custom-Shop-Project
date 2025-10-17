import { Order, ServerPaginatedResult } from "@/types";
import baseApi from "../base";

export async function getUserOrders(
  params?: Record<string, string | number | undefined>,
) {
  const res = await baseApi.get<ServerPaginatedResult<Order>>("/orders/", {
    params,
  });
  return res.data;
}

export async function getUserOrder(id: string | number) {
  const res = await baseApi.get<Order>(`/orders/${id}/`);
  return res.data;
}

export type CreateOrderPayload = {
  address_id: number;
};
export type CreateOrderResponse = {
  payment_url: string;
};
export async function createUserOrder(data: CreateOrderPayload) {
  const res = await baseApi.post<CreateOrderResponse>(
    "/orders/checkout/",
    data,
  );
  return res.data;
}
