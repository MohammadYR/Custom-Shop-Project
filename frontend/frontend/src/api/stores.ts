import { useQuery, UseQueryOptions } from "@tanstack/react-query";
import baseApi from "./base";

export type Store = {
  id: number;
  name: string;
  description: string;
  seller: string;
};
export async function getStore(storeId: string | number) {
  const res = await baseApi.get<Store>(`/stores/${storeId}/`);
  return res.data;
}

export function useStore(
  id: string | number,
  options?: Partial<UseQueryOptions<Store, Error>>,
) {
  return useQuery({
    queryFn: () => getStore(id),
    queryKey: ["store", id],
    ...options,
  });
}
