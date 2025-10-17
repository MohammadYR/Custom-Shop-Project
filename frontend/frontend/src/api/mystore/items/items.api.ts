import baseApi from "@/api/base";
import {
  ServerPaginatedResult,
  StoreItemCreate,
  StoreItemDetails,
  StoreItemQueryFilter,
} from "@/types";

export async function getMyStoreItems(params?: Partial<StoreItemQueryFilter>) {
  return baseApi
    .get<ServerPaginatedResult<StoreItemDetails>>("/mystore/items/", { params })
    .then((res) => res.data);
}

export async function getMyStoreItem(id: string | number) {
  return baseApi
    .get<StoreItemDetails>(`/mystore/items/${id}/`)
    .then((res) => res.data);
}
export async function addMyStoreItems(data: StoreItemCreate) {
  return baseApi.post("/mystore/items/", data).then((res) => res.data);
}

export async function update(data: StoreItemCreate & { id: string | number }) {
  return baseApi
    .put(`/mystore/items/${data.id}/`, data)
    .then((res) => res.data);
}

export async function deleteMyStoreItems(id: string | number) {
  return baseApi.delete(`/mystore/items/${id}/`).then((res) => res.data);
}
