import baseApi from "@/api/base";
import { AddressCreateData, AddressType } from "@/types";

export async function createStoreAddress(data: AddressCreateData) {
  const res = await baseApi.post<AddressType>(`/mystore/address/`, data);
  return res.data;
}

export async function updateStoreAddress(
  data: AddressCreateData & { id: string | number },
) {
  const res = await baseApi.put<AddressType>(
    `/mystore/address/${data.id}/`,
    data,
  );
  return res.data;
}

export async function deleteStoreAddress(addressId: string | number) {
  const res = await baseApi.delete(`/mystore/address/${addressId}/`);
  return res.data;
}

export async function getStoreAddress() {
  const res = await baseApi.get<AddressType[]>(`/mystore/address/`);
  return res.data;
}
