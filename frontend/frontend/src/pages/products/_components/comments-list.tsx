import { useReviewsQuery } from "@/api/review/review.hooks";
import { PaginationControl } from "@/components/modules/pagination-control";
import { useState } from "react";
import { Rating } from "react-simple-star-rating";

export function CommentsList({
  id,
  type = "products",
}: {
  id: string;
  type?: "products" | "stores";
}) {
  const [page, setPage] = useState(1);
  const pageSize = 5;
  const { data: reviews } = useReviewsQuery(id.toString(), type, {
    params: {
      page,
      page_size: pageSize,
    },
  });
  return (
    <div>
      <div className="flex flex-col gap-2">
        {reviews?.results.map((review) => (
          <article className="rounded-2xl border p-3" key={review.id}>
            <div className="flex justify-between">
              <div className="text-sm text-gray-600">
                {review.user.first_name} {review.user.last_name}
              </div>
              <div>
                <Rating
                  SVGclassName="inline-block w-[24px]"
                  readonly
                  initialValue={review.rating}
                />
              </div>
            </div>
            <p>{review.comment}</p>
            <div className="mt-2 text-sm text-gray-600">
              {new Date(review.created_at).toLocaleString("fa")}
            </div>
          </article>
        ))}
      </div>
      <div className="mt-2">
        <PaginationControl
          currentPage={page}
          setCurrentPage={(newPage) => setPage(newPage)}
          total={reviews?.count}
          pageSize={pageSize}
        />
      </div>
    </div>
  );
}
