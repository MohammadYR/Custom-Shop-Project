import {
  useMutation,
  useQuery,
  useQueryClient,
  UseQueryOptions,
} from "@tanstack/react-query";
import {
  createAddress,
  deleteAddress,
  getUserAddress,
  getUserInfo,
  registerStore,
  updateAddress,
  updateUserInfo,
} from "./myuser.api";
import { queryClient } from "../baseQuery";
import {
  AddressCreateData,
  MutationOptionsFromFn,
  QueryOptionsFromFn,
  UserInfo,
} from "@/types";
import { MY_STORE_KEY } from "../mystore/strore/store.hooks";
import { tokens } from "@/hooks/useAuth";
export const MY_USER_KEY = "myUser";
// User info hook
export function useUserInfo(
  options?: Partial<UseQueryOptions<UserInfo, Error>>,
) {
  return useQuery({
    queryKey: [MY_USER_KEY],
    queryFn: getUserInfo,
    enabled: !!tokens.access,
    ...options,
  });
}

export function useUpdateUserInfo(
  options?: MutationOptionsFromFn<typeof updateUserInfo>,
) {
  const { onSettled, ...rest } = options || {};
  return useMutation({
    mutationFn: updateUserInfo,
    onSettled(data, error, variables, context) {
      queryClient.invalidateQueries({
        queryKey: [MY_USER_KEY],
      });
      onSettled?.(data, error, variables, context);
    },
    ...rest,
  });
}

export function useRegisterStoreMutation(
  options?: MutationOptionsFromFn<typeof registerStore>,
) {
  return useMutation({
    mutationFn: registerStore,
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: [MY_STORE_KEY] });
      queryClient.invalidateQueries({ queryKey: [MY_USER_KEY] });
    },
    ...options,
  });
}

const USER_ADDRESS_KEY = "USER_ADDRESS";

export function useUserAddress(
  options?: QueryOptionsFromFn<typeof getUserAddress>,
) {
  return useQuery({
    queryKey: [USER_ADDRESS_KEY],
    queryFn: getUserAddress,
    ...options,
  });
}

export function useUserCreateAddress(
  options?: MutationOptionsFromFn<typeof createAddress>,
) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: AddressCreateData) => createAddress(data),
    onSettled: () =>
      queryClient.invalidateQueries({ queryKey: [USER_ADDRESS_KEY] }),
    ...options,
  });
}

export function useUserUpdateAddress(
  options?: MutationOptionsFromFn<typeof updateAddress>,
) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: updateAddress,
    onSettled: () =>
      queryClient.invalidateQueries({ queryKey: [USER_ADDRESS_KEY] }),
    ...options,
  });
}

export function useUserDeleteAddress(
  options?: MutationOptionsFromFn<typeof deleteAddress>,
) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: deleteAddress,
    onSettled: () =>
      queryClient.invalidateQueries({ queryKey: [USER_ADDRESS_KEY] }),
    ...options,
  });
}
