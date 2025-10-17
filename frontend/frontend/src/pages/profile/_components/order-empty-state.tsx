import { ShoppingBag, Package } from "lucide-react";
import { Link } from "react-router";
export const OrdersEmptyState = () => {
  return (
    <div className="flex flex-col items-center justify-center px-4 py-16 text-center">
      {/* Icon */}
      <div className="relative mb-6">
        <div className="flex h-24 w-24 items-center justify-center rounded-full bg-gray-100">
          <Package className="h-12 w-12 text-gray-400" />
        </div>
        <div className="absolute -right-2 -bottom-2 flex h-8 w-8 items-center justify-center rounded-full bg-orange-100">
          <ShoppingBag className="h-4 w-4 text-orange-500" />
        </div>
      </div>

      {/* Title */}
      <h2 className="mb-2 text-xl font-semibold text-gray-900">
        هنوز سفارشی ندارید
      </h2>

      {/* Description */}
      <p className="mb-8 max-w-sm leading-relaxed text-gray-600">
        وقتی اولین سفارش خود را ثبت کنید، جزئیات آن در اینجا نمایش داده خواهد شد
      </p>

      {/* Action Button */}
      <Link to={"/"}>
        <button className="flex cursor-pointer items-center gap-2 rounded-lg bg-blue-600 px-6 py-3 font-medium text-white transition-colors duration-200 hover:bg-blue-700">
          <ShoppingBag className="h-5 w-5" />
          شروع خرید
        </button>
      </Link>

      {/* Additional Info */}
      <div className="mt-8 text-sm text-gray-500">
        <p>می‌توانید از طریق صفحه محصولات خرید خود را آغاز کنید</p>
      </div>
    </div>
  );
};
