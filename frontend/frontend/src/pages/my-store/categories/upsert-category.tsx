import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Category } from "@/types";
import CategoryForm from "./category-form";
import { useRef } from "react";
import {
  useCreateCategory,
  useUpdateCategory,
} from "@/api/admin/categories/categories.hook";

type Props = {
  isFormOpen: boolean;
  setIsFormOpen: (open: boolean) => void;
  initialData?: Category;
};

export default function UpsertCategoryDialog({
  isFormOpen,
  setIsFormOpen,
  initialData,
}: Props) {
  const formRef = useRef<HTMLFormElement>(null);

  const { mutate: update, isPending: updatePending } = useUpdateCategory({
    onSuccess() {
      setIsFormOpen(false);
    },
  });

  const { mutate: create, isPending: createPending } = useCreateCategory({
    onSuccess() {
      setIsFormOpen(false);
    },
  });

  const isPending = updatePending || createPending;

  const handleSubmit = (formData: FormData) => {
    if (initialData?.id) {
      formData.append("id", String(initialData.id));
      update(formData);
    } else {
      create(formData);
    }
  };

  return (
    <Dialog open={isFormOpen} onOpenChange={setIsFormOpen}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle>
            {initialData
              ? "ویرایش دسته (Edit Category)"
              : "ایجاد دسته جدید (Create New Category)"}
          </DialogTitle>
          {initialData && (
            <DialogDescription>شناسه دسته: {initialData.id}</DialogDescription>
          )}
        </DialogHeader>

        <CategoryForm
          ref={formRef}
          onSubmit={handleSubmit}
          initialData={initialData}
        />

        <DialogFooter className="mt-4">
          <Button
            variant="outline"
            onClick={() => setIsFormOpen(false)}
            disabled={isPending}
          >
            لغو (Cancel)
          </Button>
          <Button
            onClick={() => formRef.current?.requestSubmit()}
            disabled={isPending}
          >
            {isPending ? "در حال ثبت..." : "ثبت (Submit)"}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
