import { useMutation, useQueryClient } from "@tanstack/react-query";

import { requestOtp, verifyOtp } from "./auth.api";
import { MutationOptionsFromFn } from "@/types";
import { MY_USER_KEY } from "@/api/myuser/myuser.hooks";

// Login hook
export function useRequestOtp(
  options?: MutationOptionsFromFn<typeof requestOtp>,
) {
  const queryClient = useQueryClient();
  return useMutation({
    ...options,
    mutationFn: requestOtp,
    onSettled(...args) {
      queryClient.invalidateQueries({ queryKey: [MY_USER_KEY] });
      options?.onSettled?.(...args);
    },
  });
}

// Register hook
export function useVerifyOtp(
  options?: MutationOptionsFromFn<typeof verifyOtp>,
) {
  const queryClient = useQueryClient();
  return useMutation({
    ...options,
    mutationFn: verifyOtp,
    onSettled(...args) {
      queryClient.invalidateQueries({ queryKey: [MY_USER_KEY] });
      options?.onSettled?.(...args);
    },
  });
}
