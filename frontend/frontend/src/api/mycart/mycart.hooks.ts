import {
  useQuery,
  useMutation,
  UseMutationOptions,
} from "@tanstack/react-query";
import {
  getUserCart,
  addProductToCart,
  updateCartItemQuantity,
  removeCartItem,
  getUserCartItems,
} from "./mycart.api";
import { CartItem, QueryOptionsFromFn } from "@/types";
import { queryClient } from "../baseQuery";
import { useUserInfo } from "../myuser/myuser.hooks";

const CART_QUERY_KEY = "MY_CART";

export function useCart(options?: QueryOptionsFromFn<typeof getUserCart>) {
  const { data: userInfo } = useUserInfo();
  return useQuery({
    queryKey: [CART_QUERY_KEY],
    queryFn: getUserCart,
    enabled: !!userInfo,
    ...options,
  });
}
export function useCartItems(
  options?: QueryOptionsFromFn<typeof getUserCartItems>,
) {
  const { data: userInfo } = useUserInfo();
  return useQuery({
    queryKey: [CART_QUERY_KEY, "items"],
    queryFn: getUserCartItems,
    enabled: !!userInfo,
    ...options,
  });
}

export function useAddToCart(
  options?: UseMutationOptions<void, Error, number | string>,
) {
  return useMutation({
    mutationFn: addProductToCart,
    onSettled: () =>
      queryClient.invalidateQueries({ queryKey: [CART_QUERY_KEY] }),
    ...options,
  });
}

export function useUpdateCartItem(
  options?: UseMutationOptions<
    void,
    Error,
    { id: number | string; quantity: number },
    { previousCart: CartItem[] | undefined }
  >,
) {
  return useMutation({
    mutationFn: ({ id, quantity }) => updateCartItemQuantity(id, quantity),
    onSettled: () =>
      queryClient.invalidateQueries({ queryKey: [CART_QUERY_KEY] }),
    ...options,
  });
}

export function useRemoveCartItem(
  options?: UseMutationOptions<
    void,
    Error,
    number | string,
    { previousCart?: CartItem[] }
  >,
) {
  return useMutation({
    mutationFn: removeCartItem,
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: [CART_QUERY_KEY] });
    },
    ...options,
  });
}
