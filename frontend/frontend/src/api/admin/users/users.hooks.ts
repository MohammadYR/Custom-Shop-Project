import {
  getAllUsers,
  getUser,
  createUser,
  updateUser,
  deleteUser,
} from "./users.api";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import type {
  MutationOptionsFromFn,
  QueryOptionsFromFn,
  UserQueryFilter,
} from "@/types";

// Fetch all users
export function useUsers(
  params?: Partial<UserQueryFilter>,
  options?: QueryOptionsFromFn<typeof getAllUsers>,
) {
  return useQuery({
    queryKey: ["admin", "users", params],
    queryFn: () => getAllUsers(params),
    ...options,
  });
}

// Fetch single user
export function useUser(
  id: string | number,
  options?: QueryOptionsFromFn<typeof getUser>,
) {
  return useQuery({
    queryKey: ["admin", "users", id],
    queryFn: () => getUser(id),
    enabled: !!id,
    ...options,
  });
}

// Create user
export function useCreateUser(
  options?: MutationOptionsFromFn<typeof createUser>,
) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: createUser,
    onSettled: (...args) => {
      queryClient.invalidateQueries({ queryKey: ["admin", "users"] });
      options?.onSettled?.(...args);
    },
    ...options,
  });
}

// Update user
export function useUpdateUser(
  options?: MutationOptionsFromFn<typeof updateUser>,
) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: updateUser,
    onSettled: (...args) => {
      queryClient.invalidateQueries({ queryKey: ["admin", "users"] });
      options?.onSettled?.(...args);
    },
    ...options,
  });
}

// Delete user
export function useDeleteUser(
  options?: MutationOptionsFromFn<typeof deleteUser>,
) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: deleteUser,
    onSettled: (...args) => {
      queryClient.invalidateQueries({ queryKey: ["admin", "users"] });
      options?.onSettled?.(...args);
    },
    ...options,
  });
}
