import { Review, ServerPaginatedResult } from "@/types";
import baseApi from "../base";
import { AxiosRequestConfig } from "axios";

export async function createReview(
  id: string,
  type: "products" | "stores" = "products",
  data: { rating: number; comment: string },
) {
  const url = `/${type}/${id}/review_create/`;
  const res = await baseApi.post(url, data);
  return res.data;
}

export async function getReviews(
  productId: string,
  type: "products" | "stores" = "products",
  params?: AxiosRequestConfig["params"],
) {
  const url = `/${type}/${productId}/review_list/`;
  const res = await baseApi.get<ServerPaginatedResult<Review>>(url, {
    params,
  });
  return res.data;
}
