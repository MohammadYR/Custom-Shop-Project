import { useOrderQuery } from "@/api/orders/orders.hooks";
import { showJalaliDate, showPersianNumber } from "@/lib/utils";
import { OrderStatusDescriptionMap } from "@/types";
import { Link, useParams } from "react-router";
import { CommentForm } from "../products/_components/comment-form";
import { Button } from "@/components/ui/button";

export default function Order() {
  const { orderId } = useParams();
  const { data: order, isError, isLoading } = useOrderQuery(orderId!);
  if (isError) {
    return "...error";
  }
  if (isLoading || !order) {
    return "...loading";
  }

  return (
    <div className="rounded-2xl border p-3">
      <div className="p-3">
        <div>جزئیات سفارش</div>
      </div>
      <div key={order.id} className="rounded-sm border p-3">
        <div>وضعیت سفارش: {OrderStatusDescriptionMap[order.status]}</div>
        <hr className="my-4" />
        <div className="mt-2 flex gap-1.5">
          <div>{showJalaliDate(order.updated_at)}</div>
          <div>کد سفارش:{order.id}</div>
          <div>مبلغ :{showPersianNumber(order.total_price)} تومان</div>
        </div>
        <hr className="my-2" />
        <div>
          آدرس: {order.address.city} {order.address.address_line_1}{" "}
          {order.address.address_line_2}
        </div>
        <div className="mt-4 flex flex-col gap-4">
          {order.items.map((item) => (
            <div
              key={item.id}
              className="flex items-end justify-between gap-4 p-3 not-last-of-type:border-b"
            >
              <Link
                to={`/products/${item.store_item.product.id}`}
                className="flex gap-1.5"
              >
                <div className="size-32">
                  <img
                    className="size-32"
                    alt={item.store_item.product.name}
                    src={item.store_item.product.images[0].image}
                  />
                </div>
                <div className="flex flex-col">
                  <div className="grow text-xl">
                    {item.store_item.product.name}
                  </div>
                  <div className="text-sm">تعداد: {item.quantity}</div>
                  <div className="text-sm">قیمت: {item.total_price}</div>
                </div>
              </Link>

              <div>
                <CommentForm
                  id={item.store_item.product.id}
                  renderButton={(setOpen) => (
                    <Button
                      className="mt-2 w-full"
                      variant="outline"
                      onClick={() => setOpen(true)}
                    >
                      ثبت دیدگاه
                    </Button>
                  )}
                />
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
