import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { OrderStatusDescriptionMap, ShopOrder } from "@/types";
import { ChangeOrderStatusDialog } from "./ChangeOrderStatusDialog";

type Props = {
  orders: ShopOrder[];
};

export default function OrdersTable({ orders }: Props) {
  return (
    <div className="space-y-4">
      <Table>
        <TableHeader>
          <TableRow className="**:text-right">
            <TableHead>کد سفارش</TableHead>
            <TableHead>وضعیت</TableHead>
            <TableHead>نام کالا</TableHead>
            <TableHead>تعداد</TableHead>
            <TableHead>قیمت محصول</TableHead>
            <TableHead>قیمت کل</TableHead>
            <TableHead>مشتری</TableHead>
            <TableHead>عملیات</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {orders.map((order) => (
            <TableRow key={order.id}>
              <TableCell>{order.id}</TableCell>
              <TableCell>{OrderStatusDescriptionMap[order.status]}</TableCell>
              <TableCell>{order.store_item.product.name}</TableCell>
              <TableCell>{order.quantity}</TableCell>
              <TableCell>{order.price}</TableCell>
              <TableCell>{order.total_price} تومان</TableCell>
              <TableCell>
                {order.user.first_name + " " + order.user.last_name}
              </TableCell>
              <TableCell>
                <ChangeOrderStatusDialog order={order} />
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </div>
  );
}
