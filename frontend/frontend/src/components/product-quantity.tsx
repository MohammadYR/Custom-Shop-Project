import { CartItem } from "@/types";
import { Button } from "./ui/button";
import {
  useRemoveCartItem,
  useUpdateCartItem,
} from "@/api/mycart/mycart.hooks";

export function ProductQuantity({ cartItem }: { cartItem: CartItem }) {
  const { mutate: changeItem, isPending: isPending1 } = useUpdateCartItem();
  const { mutate: deleteItem, isPending: isPending2 } = useRemoveCartItem();
  const isPending = isPending1 || isPending2;

  return (
    <div className="flex items-center gap-2">
      <Button
        variant={"outline"}
        size={"icon"}
        className="text-gray-500 hover:text-gray-700"
        disabled={isPending}
        onClick={() => {
          if (cartItem.quantity < 2) {
            deleteItem(cartItem.id);
          } else {
            changeItem({ id: cartItem.id, quantity: cartItem.quantity - 1 });
          }
        }}
      >
        -
      </Button>
      <span className="text-sm font-medium">{cartItem.quantity}</span>
      <Button
        disabled={isPending}
        variant={"outline"}
        size={"icon"}
        className="text-gray-500 hover:text-gray-700"
        onClick={() =>
          changeItem({ id: cartItem.id, quantity: cartItem.quantity + 1 })
        }
      >
        +
      </Button>
    </div>
  );
}
