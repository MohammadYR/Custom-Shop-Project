import baseApi from "@/api/base";
import { ServerPaginatedResult, UserInfo, UserQueryFilter } from "@/types";

// Get all users with optional filters
export async function getAllUsers(params?: Partial<UserQueryFilter>) {
  const res = await baseApi.get<ServerPaginatedResult<UserInfo>>(
    "/admin/users/",
    { params },
  );
  return res.data;
}

// Get a single user by ID
export async function getUser(id: string | number) {
  const res = await baseApi.get<UserInfo>(`/admin/users/${id}/`);
  return res.data;
}

// Create a new user (omit "id" if it's auto-generated)
export async function createUser(data: Omit<UserInfo, "id">) {
  const res = await baseApi.post<UserInfo>("/admin/users/", data);
  return res.data;
}

// Update an existing user
export async function updateUser(data: UserInfo) {
  const res = await baseApi.put<UserInfo>(`/admin/users/${data.id}/`, data);
  return res.data;
}

// Delete a user by ID
export async function deleteUser(id: string | number) {
  const res = await baseApi.delete(`/admin/users/${id}/`);
  return res.data;
}
