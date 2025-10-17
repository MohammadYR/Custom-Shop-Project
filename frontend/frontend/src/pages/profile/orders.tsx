import { useOrdersQuery } from "@/api/orders/orders.hooks";
import { PaginationControl } from "@/components/modules/pagination-control";
import { cn, showJalaliDate, showPersianNumber } from "@/lib/utils";
import { Order, OrderStatus, OrderStatusDescriptionMap } from "@/types";
import { Link, useSearchParams } from "react-router";
import { OrdersEmptyState } from "./_components/order-empty-state";

export default function Orders() {
  const [search] = useSearchParams();
  const status = search.get("status") || OrderStatus.PENDING;
  const { data: orders, isLoading } = useOrdersQuery({ status }); // todo: add orders params
  return (
    <div className="rounded-2xl border">
      <div className="p-3">
        <div>تاریخچه سفارشات</div>
        <ul className="mt-2 flex gap-3 text-sm">
          <li
            className={cn(
              status === "1" && "border-b-2 border-b-red-400",
              "p-2",
            )}
          >
            <Link to={`?status=${OrderStatus.PENDING}`}>
              {OrderStatusDescriptionMap[OrderStatus.PENDING]}
            </Link>
          </li>
          <li
            className={cn(
              status === "2" && "border-b-2 border-b-red-400",
              "p-2",
            )}
          >
            <Link to={`?status=${OrderStatus.PROCESSING}`}>
              {OrderStatusDescriptionMap[OrderStatus.PROCESSING]}
            </Link>
          </li>
          <li
            className={cn(
              status === "3" && "border-b-2 border-b-red-400",
              "p-2",
            )}
          >
            <Link to={`?status=${OrderStatus.DELIVERED}`}>
              {OrderStatusDescriptionMap[OrderStatus.DELIVERED]}
            </Link>
          </li>
          <li
            className={cn(
              status === "4" && "border-b-2 border-b-red-400",
              "p-2",
            )}
          >
            <Link to={`?status=${OrderStatus.CANCELLED}`}>
              {OrderStatusDescriptionMap[OrderStatus.CANCELLED]}
            </Link>
          </li>
          <li
            className={cn(
              status === "5" && "border-b-2 border-b-red-400",
              "p-2",
            )}
          >
            <Link to={`?status=${OrderStatus.FAILED}`}>
              {OrderStatusDescriptionMap[OrderStatus.FAILED]}
            </Link>
          </li>
        </ul>
      </div>
      <hr className="" />
      <div className="flex flex-col gap-2 p-3">
        {isLoading
          ? Array(4)
              .fill(1)
              .map((_, index) => <OrderCardSkeleton key={index} />)
          : orders?.results.map((order) => (
              <OrderCard order={order} key={order.id} />
            ))}
        {orders?.count === 0 && <OrdersEmptyState />}
      </div>
      <PaginationControl
        currentPage={1}
        setCurrentPage={() => {}}
        pageSize={5}
        total={0}
      />
    </div>
  );
}

const OrderCard = ({ order }: { order: Order }) => (
  <Link
    to={`/profile/orders/${order.id}`}
    key={order.id}
    className="block rounded-sm border p-3"
  >
    <div>وضعیت سفارش: {OrderStatusDescriptionMap[order.status]}</div>
    <div className="mt-2 flex gap-1.5">
      <div>{showJalaliDate(order.updated_at)}</div>
      <div>کد سفارش:{order.id}</div>
      <div>مبلغ :{showPersianNumber(order.total_price)} تومان</div>
    </div>
    <div className="mt-4 flex gap-4">
      {order.items.map((item) => (
        <div key={item.id}>
          <img
            width={85}
            height={85}
            alt={item.store_item.product.name}
            src={item.store_item.product.images[0].image}
          />
        </div>
      ))}
    </div>
  </Link>
);

const OrderCardSkeleton = () => {
  return (
    <div className="block animate-pulse rounded-sm border p-3">
      {/* Order Status */}
      <div className="h-4 w-32 rounded bg-gray-200"></div>

      {/* Order Details Row */}
      <div className="mt-2 flex gap-1.5">
        <div className="h-4 w-20 rounded bg-gray-200"></div>
        <div className="h-4 w-24 rounded bg-gray-200"></div>
        <div className="h-4 w-28 rounded bg-gray-200"></div>
      </div>

      {/* Product Images */}
      <div className="mt-4 flex gap-4">
        {[...Array(3)].map((_, index) => (
          <div
            key={index}
            className="h-[85px] w-[85px] rounded bg-gray-200"
          ></div>
        ))}
      </div>
    </div>
  );
};
