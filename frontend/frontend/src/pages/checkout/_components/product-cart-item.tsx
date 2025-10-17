import { ProductQuantity } from "@/components/product-quantity";
import { CartItem } from "@/types";

export function ProductCartItem({ cartItem }: { cartItem: CartItem }) {
  return (
    <div className="flex items-center justify-between border-b py-2">
      <div className="flex items-center gap-2">
        <img
          src={cartItem.product.images[0]?.image}
          alt="product"
          className="h-24 w-24 rounded-md object-cover"
        />
        <div className="flex flex-col">
          <span className="text-sm font-medium">{cartItem.product.name}</span>
          <span className="text-xs text-gray-500">
            {cartItem.product.description}
          </span>
        </div>
      </div>
      <div>
        <ProductQuantity cartItem={cartItem} />
        <div className="flex items-center gap-2">
          <span className="text-sm font-medium">
            {cartItem.total_price.toLocaleString("fa")}
          </span>
          <button className="text-red-500 hover:text-red-700">حذف</button>
        </div>
      </div>
    </div>
  );
}
