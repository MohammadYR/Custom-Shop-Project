import { useAddToCart, useCartItems } from "@/api/mycart/mycart.hooks";
import { ProductQuantity } from "@/components/product-quantity";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import { ProductDetails } from "@/types";
import { Link } from "react-router";

export function ProductSellerRow({
  seller,
}: {
  seller: ProductDetails["sellers"][0];
}) {
  const { data: cartItems, isLoading } = useCartItems();
  const { mutate: addToCart } = useAddToCart();
  const isProductInCart = !!cartItems?.find(
    (item) => item.product.id === seller.product,
  );
  const cartItem = cartItems?.find(
    (item) => isProductInCart && item.store.id === seller.store.id,
  );

  return (
    <div className="my-4 flex justify-between border-b p-4">
      <div>
        <Link to={"/stores/" + seller.store.id}>{seller.store.name}</Link>
      </div>
      <div>
        <div className="flex items-end gap-1">
          <div>
            <div
              className={cn(
                !!seller.discount_price && "text-sm text-gray-400 line-through",
              )}
            >
              {(+seller.price).toLocaleString("fa")}
            </div>
            {seller.discount_price && (
              <div>{(+seller.discount_price).toLocaleString("fa")}</div>
            )}
          </div>
          <div>تومان</div>
        </div>
      </div>
      <div>
        {cartItem ? (
          <ProductQuantity cartItem={cartItem} />
        ) : (
          <Button
            disabled={isLoading || !!isProductInCart}
            onClick={() => {
              addToCart(seller.id);
            }}
          >
            افزودن به سبد خرید
          </Button>
        )}
      </div>
    </div>
  );
}
