import { useCart } from "@/api/mycart/mycart.hooks";
import { Button } from "@/components/ui/button";
import { showPersianNumber } from "@/lib/utils";

export function CartSummery({ onClick }: { onClick?: () => void }) {
  const { data } = useCart();

  return (
    <div className="md:sticky md:top-34">
      <div className="mt-4 rounded-2xl border p-4 md:m-4 md:w-[300px]">
        <div className="flex items-center justify-between p-2">
          <span className="text-sm font-medium">جمع کل</span>
          <span className="text-sm font-medium">
            {showPersianNumber(data?.total_price || 0)} تومان
          </span>
        </div>
        <div className="flex items-center justify-between p-2">
          <span className="text-sm font-medium">مجموع تخفیف ها</span>
          <span className="text-sm font-medium">300,000 تومان</span>
        </div>
        <div className="flex items-center justify-between p-2">
          <span className="text-sm font-medium">هزینه ارسال</span>
          <span className="text-sm font-medium">
            {showPersianNumber("100000")} تومان
          </span>
        </div>
        <hr className="m-4" />
        <div className="flex items-center justify-between p-2">
          <span className="text-sm font-medium">جمع مبلغ قابل پرداخت</span>
          <span className="text-sm font-medium">
            {showPersianNumber(data?.total_price || "0")} تومان
          </span>
        </div>
        <div className="p-2">
          <Button onClick={onClick} type="submit" className="w-full text-white">
            ثبت سفارش
          </Button>
        </div>
      </div>
    </div>
  );
}
