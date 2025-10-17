import {
  AddressCreateData,
  MutationOptionsFromFn,
  QueryOptionsFromFn,
} from "@/types";
import {
  createStoreAddress,
  deleteStoreAddress,
  getStoreAddress,
  updateStoreAddress,
} from "./address.api";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

const MY_STORE_ADDRESS = "my_store_address";

export function useCreateStoreAddress(
  options?: MutationOptionsFromFn<typeof createStoreAddress>,
) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: AddressCreateData) => createStoreAddress(data),
    onSettled: () =>
      queryClient.invalidateQueries({ queryKey: [MY_STORE_ADDRESS] }),
    ...options,
  });
}

export function useStoreUpdateAddress(
  options?: MutationOptionsFromFn<typeof updateStoreAddress>,
) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: updateStoreAddress,
    onSettled: () =>
      queryClient.invalidateQueries({ queryKey: [MY_STORE_ADDRESS] }),
    ...options,
  });
}

export function useStoreDeleteAddress(
  options?: MutationOptionsFromFn<typeof deleteStoreAddress>,
) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: deleteStoreAddress,
    onSettled: () =>
      queryClient.invalidateQueries({ queryKey: [MY_STORE_ADDRESS] }),
    ...options,
  });
}

export function useMyStoreAddress(
  options?: QueryOptionsFromFn<typeof getStoreAddress>,
) {
  return useQuery({
    queryFn: getStoreAddress,
    queryKey: [MY_STORE_ADDRESS],
    ...options,
  });
}
