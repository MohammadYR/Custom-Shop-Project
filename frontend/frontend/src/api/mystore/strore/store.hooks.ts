import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { MutationOptionsFromFn, QueryOptionsFromFn } from "@/types";
import { getMyStore, updateMyStore } from "./store.api";
export const MY_STORE_KEY = "my-store";
export function useMyStoreQuery(
  options?: QueryOptionsFromFn<typeof getMyStore>,
) {
  return useQuery({
    queryFn: getMyStore,
    queryKey: [MY_STORE_KEY],
    ...options,
  });
}

export function useUpdateMyStoreQuery(
  options?: MutationOptionsFromFn<typeof updateMyStore>,
) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: updateMyStore,
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: [MY_STORE_KEY] });
    },
    ...options,
  });
}
