import { Button } from "@/components/ui/button";
import { Rating } from "react-simple-star-rating";
import { CommentForm } from "./comment-form";

export function CommentBox({
  id,
  type = "products",
  rating,
}: {
  id: string;
  type?: "stores" | "products";
  rating?: number | null;
}) {
  const objectName = type === "products" ? "کالا" : "فروشگاه";
  return (
    <div className="rounded-2xl border p-4">
      <div className="text-primary text-xl">امتیاز و دیدگاه کاربران</div>
      {rating && <div>{rating?.toLocaleString("fa")} از ۵</div>}
      {rating && (
        <div>
          <Rating
            SVGclassName="inline-block w-[24px]"
            allowFraction
            readonly
            initialValue={rating}
          />
        </div>
      )}
      <div className="mt-1 text-sm">
        شما هم درباره این {objectName} دیدگاه ثبت کنید
      </div>
      <CommentForm
        type={type}
        id={id}
        renderButton={(setOpen) => (
          <Button
            className="mt-2 w-full"
            variant={"outline"}
            onClick={() => setOpen(true)}
          >
            ثبت دیدگاه
          </Button>
        )}
      />
    </div>
  );
}
