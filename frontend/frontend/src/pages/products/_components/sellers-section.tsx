import { ProductDetails } from "@/types";
import { ProductSellerRow } from "./seller-row";

export default function SellersSection({
  sellers,
}: {
  sellers: ProductDetails["sellers"];
}) {
  if (sellers.length < 2) {
    return null;
  }
  return (
    <section>
      <span className="border-primary m-2 inline-block border-b-2 pb-2">
        فروشندگان این کالا
      </span>
      {sellers.map((seller) => (
        <ProductSellerRow seller={seller} key={seller.id} />
      ))}
    </section>
  );
}
