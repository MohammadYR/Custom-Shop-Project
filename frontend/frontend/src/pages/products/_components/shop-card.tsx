import { useAddToCart, useCartItems } from "@/api/mycart/mycart.hooks";
import { ProductQuantity } from "@/components/product-quantity";
import { Button } from "@/components/ui/button";
import { ProductDetails } from "@/types";

export default function ShopCard({ product }: { product: ProductDetails }) {
  const { data: cartItems } = useCartItems();
  const { mutate: addToCart } = useAddToCart();
  const cartItem = cartItems?.find((item) => item.product.id === product.id);

  const isProductInCart = !!cartItem;
  if (!product.best_seller) {
    return (
      <div className="flex shrink-0 flex-col gap-4 rounded-xl border p-4 md:w-2xs">
        این محصول فروشنده ای ندارد
      </div>
    );
  }

  return (
    <div className="flex shrink-0 flex-col gap-4 rounded-xl border p-4 md:w-2xs">
      <div>فروشنده</div>
      <div>
        {cartItem ? cartItem.store.name : product.best_seller.store.name}
      </div>
      <div>
        {cartItem
          ? cartItem.unit_price.toLocaleString("fa")
          : (+product.best_price).toLocaleString("fa")}{" "}
        تومان
      </div>
      {isProductInCart && cartItem ? (
        <ProductQuantity cartItem={cartItem} />
      ) : (
        <Button
          disabled={isProductInCart}
          className="w-full"
          onClick={() => addToCart(product.best_seller!.id)}
        >
          افزودن به سبد خرید
        </Button>
      )}
    </div>
  );
}
