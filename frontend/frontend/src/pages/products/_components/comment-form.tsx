import { useReviewMutation } from "@/api/review/review.hooks";
import {
  AlertDialog,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "@/components/ui/alert-dialog";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Dispatch, ReactNode, SetStateAction, useRef, useState } from "react";
import { Rating } from "react-simple-star-rating";

type CommentFormProps = {
  id: string | number;
  renderButton?: (setOpen: Dispatch<SetStateAction<boolean>>) => ReactNode;
  type?: "stores" | "products";
};
export function CommentForm({ id, renderButton, type }: CommentFormProps) {
  const [rating, setRating] = useState(1);
  const [open, setOpen] = useState(false);
  const [comment, setComment] = useState("");
  const formRef = useRef<HTMLFormElement>(null);
  // Catch Rating value
  const handleRating = (rate: number) => {
    setRating(rate);
  };
  const { mutateAsync: createReview } = useReviewMutation(id.toString(), type);
  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const review = {
      rating: rating,
      comment: comment,
    };
    try {
      await createReview(review);
      setOpen(false);
    } catch (err) {
      console.log(err);
    }
  };
  return (
    <>
      {renderButton?.(setOpen)}
      <AlertDialog open={open} onOpenChange={setOpen}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>
              نظر خود را با ما در میان بگذارید
            </AlertDialogTitle>
            <form ref={formRef} onSubmit={handleSubmit}>
              <AlertDialogDescription>
                <Rating
                  initialValue={1}
                  onClick={handleRating}
                  SVGclassName="inline-block w-[24px]"
                />
                <span className="mt-2">
                  <Textarea
                    value={comment}
                    onChange={(e) => setComment(e.target.value)}
                    placeholder="نظر خود را وارد کنید"
                  />
                </span>
              </AlertDialogDescription>
            </form>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel onClick={() => setOpen(false)}>
              انصراف
            </AlertDialogCancel>
            <Button
              type="submit"
              onClick={() => {
                if (formRef.current) {
                  formRef.current.requestSubmit();
                }
              }}
            >
              ثبت نظر
            </Button>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </>
  );
}
