import { useState } from "react";
import OrdersTable from "./order-table";
import {
  Card,
  CardContent,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { PaginationControl } from "@/components/modules/pagination-control";
import { useStoreOrders } from "@/api/mystore/orders/hooks";

export default function CategoriesAdminPage() {
  const [page, setPage] = useState(1);
  const { data: orders } = useStoreOrders({ page });

  return (
    <Card>
      <CardHeader>
        <CardTitle>سفارش ها</CardTitle>
      </CardHeader>
      <CardContent>
        <OrdersTable orders={orders?.results ?? []} />
      </CardContent>
      <CardFooter>
        <PaginationControl
          setCurrentPage={setPage}
          pageSize={10}
          currentPage={page}
        />
      </CardFooter>
    </Card>
  );
}
