import { ProductDetails } from "@/types";

export function ProductOverview({ product }: { product: ProductDetails }) {
  return (
    <div className="grow">
      <div className="text-primary border-b pb-2 text-xl">مشخصات محصول</div>
      <ul className="mt-2 flex flex-col gap-2">
        <li className="flex items-center gap-2">
          <div className="text-gray-600">نام: </div>
          <div>{product.name}</div>
        </li>
      </ul>
      <div className="">
        <div className="text-gray-600">توضیحات: </div>
        <div>{product.description}</div>
      </div>
    </div>
  );
}
