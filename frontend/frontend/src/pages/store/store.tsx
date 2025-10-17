import { useStore } from "@/api/stores";
import { PaginationControl } from "@/components/modules/pagination-control";
import { ProductCard } from "@/components/product-card";
import Container from "@/components/ui/container";
import { StoreIcon } from "lucide-react";
import { useState } from "react";
import { useParams } from "react-router";
import { CommentsList } from "../products/_components/comments-list";
import { CommentBox } from "../products/_components/comment-box";
import { useProducts } from "@/api/products/products.hooks";

export default function Store() {
  const { storeId } = useParams();
  const [page, setPage] = useState(1);
  const { data: products } = useProducts();
  const { data: store } = useStore(storeId || "", {
    enabled: !!storeId,
  });
  return (
    <Container>
      <div className="flex rounded-2xl border p-6">
        <div className="rounded-lg border p-6">
          <StoreIcon />
        </div>
        <div>
          <div className="p-2">{store?.name}</div>
          <div className="p-2">{store?.description}</div>
        </div>
      </div>
      <div className="my-4">
        <div className="grid grow grid-cols-3 gap-2 md:grid-cols-4">
          {products?.results.map((item) => (
            <ProductCard
              key={item.id}
              id={item.id.toString()}
              image={item.images[0]?.image}
              best_seller={item.best_seller}
              name={item.name}
            />
          ))}
        </div>
        <PaginationControl
          currentPage={page}
          setCurrentPage={(newPage) => setPage(newPage)}
          total={products?.count}
        />
      </div>
      <section>
        <div className="flex gap-3">
          <CommentBox id={storeId || ""} type="stores" />
          <div className="grow">
            <CommentsList id={storeId!} type="stores" />
          </div>
        </div>
      </section>
    </Container>
  );
}
