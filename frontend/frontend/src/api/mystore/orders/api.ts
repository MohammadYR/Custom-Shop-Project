import baseApi from "@/api/base";
import { PaginateQuery, ServerPaginatedResult, ShopOrder } from "@/types";

export const ordersApi = {
  getAll: async (
    params: Partial<PaginateQuery>,
  ): Promise<ServerPaginatedResult<ShopOrder>> => {
    const res = await baseApi.get("/mystore/orderitems/", { params });
    return res.data;
  },

  getOne: async (id: string | number): Promise<ShopOrder> => {
    const res = await baseApi.get(`/mystore/orderitems/${id}/`);
    return res.data;
  },

  changeStatus: async (data: { id: string | number; status: number }) => {
    const res = await baseApi.post(
      `/mystore/orderitems/change-status/${data.id}/`,
      data,
    );
    return res.data;
  },
};
