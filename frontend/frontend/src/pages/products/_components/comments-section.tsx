import { ProductDetails } from "@/types";
import { CommentBox } from "./comment-box";
import { CommentsList } from "./comments-list";
import ShopCard from "./shop-card";
import useScrollTrigger from "@/hooks/useScrollTrigger";
import { cn } from "@/utils";

export default function CommentsSection({
  product,
}: {
  product: ProductDetails;
}) {
  const isScroll = useScrollTrigger({
    threshold: 100,
  });
  return (
    <section data-test-id={"comments"} className="flex flex-row gap-2">
      <div className="hidden md:block">
        <div
          className={cn("sticky top-34 transition-all", isScroll && "top-28")}
        >
          <CommentBox id={product.id.toString()} rating={product.rating} />
        </div>
      </div>
      <div className="grow">
        <CommentsList id={product.id.toString()} />
      </div>
      <div className="hidden md:block">
        <div
          className={cn("sticky top-34 transition-all", isScroll && "top-28")}
        >
          <ShopCard product={product} />
        </div>
      </div>
    </section>
  );
}
