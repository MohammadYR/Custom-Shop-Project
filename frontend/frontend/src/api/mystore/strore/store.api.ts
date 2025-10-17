import { RegisterStoreData, Store } from "@/types";
import baseApi from "@/api/base";

export async function getMyStore() {
  const res = await baseApi.get<Store>("/mystore/");
  return res.data;
}

export async function updateMyStore(data: RegisterStoreData) {
  const res = await baseApi.put<Store>("/mystore/", data);
  return res.data;
}
