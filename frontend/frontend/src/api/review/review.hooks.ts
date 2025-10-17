import { useQuery, UseQueryOptions } from "@tanstack/react-query";
import { ServerPaginatedResult, Review } from "@/types";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { AxiosRequestConfig } from "axios";
import { createReview, getReviews } from "./review.api";

export function useReviewsQuery(
  id: string,
  type: "products" | "stores" = "products",
  options?: Partial<UseQueryOptions<ServerPaginatedResult<Review>, Error>> & {
    params?: AxiosRequestConfig["params"];
  },
) {
  const { params, ...restOptions } = options || {};
  return useQuery<ServerPaginatedResult<Review>>({
    queryKey: [
      type === "products" ? "product-reviews" : "store-reviews",
      id,
      params,
    ],
    queryFn: () => getReviews(id, type, params),
    enabled: !!id,
    ...restOptions,
  });
}

export function useReviewMutation(
  id: string,
  type: "products" | "stores" = "products",
) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: { rating: number; comment: string }) =>
      createReview(id, type, data),
    onSettled: () => {
      queryClient.invalidateQueries({
        queryKey: [
          type === "products" ? "product-reviews" : "store-reviews",
          id,
        ],
      });
    },
  });
}
