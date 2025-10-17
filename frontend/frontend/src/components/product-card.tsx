import { cn } from "@/lib/utils";
import { Seller } from "@/types";
import { Link } from "react-router";

type Props = {
  name: string;
  best_seller: Seller | null;
  id: string;
  image: string;
  className?: string;
};
export function ProductCard({
  name,
  id,
  best_seller,
  image,
  className,
}: Props & { image: string }) {
  return (
    <Link
      to={`/products/${id}`}
      className={cn("rounded-md border border-gray-200 p-2", className)}
    >
      <img
        src={image}
        alt={name}
        className="h-40 w-full rounded-md object-cover"
      />
      <div className="product-info mt-3">
        <h2>{name}</h2>
        {best_seller ? <ProductPrice seller={best_seller} /> : "ناموجود"}
      </div>
    </Link>
  );
}

const ProductPrice = ({ seller }: { seller: Seller }) => {
  if (seller.discount_price)
    return (
      <div>
        <del className="text-sm text-gray-500">
          {(+seller.price).toLocaleString("fa-IR")}
        </del>
        <p className="text-md font-semibold">
          {(+seller.discount_price).toLocaleString("fa-IR")} تومان
        </p>
      </div>
    );

  return (
    <p className="text-md font-semibold">
      {(+seller.price).toLocaleString("fa-IR")} تومان
    </p>
  );
};
