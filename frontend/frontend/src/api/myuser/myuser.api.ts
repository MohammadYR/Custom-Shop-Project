import {
  AddressCreateData,
  AddressType,
  RegisterStoreData,
  UserInfo,
  UserUpdateProfile,
} from "@/types";
import baseApi from "../base";

export async function getUserInfo() {
  const res = await baseApi.get<UserInfo>("/myuser/");
  return res.data;
}

export async function updateUserInfo(data: UserUpdateProfile) {
  const res = await baseApi.put<UserInfo>("/myuser/", data);
  return res.data;
}

export async function registerStore(data: RegisterStoreData) {
  const res = await baseApi.post<{ details: string }>(
    "/myuser/register_as_seller/",
    data,
  );
  return res.data;
}

export async function createAddress(data: AddressCreateData) {
  const res = await baseApi.post<AddressType>(`/myuser/address/`, data);
  return res.data;
}

export async function updateAddress(
  data: AddressCreateData & { id: string | number },
) {
  const res = await baseApi.put<AddressType>(
    `/myuser/address/${data.id}/`,
    data,
  );
  return res.data;
}

export async function deleteAddress(addressId: string | number) {
  const res = await baseApi.delete(`/myuser/address/${addressId}/`);
  return res.data;
}

export async function getUserAddress() {
  const res = await baseApi.get<AddressType[]>(`/myuser/address/`);
  return res.data;
}
