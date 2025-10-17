import { useDeleteCategory } from "@/api/admin/categories/categories.hook";
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
type Props = {
  isFormOpen: boolean;
  setIsFormOpen: (open: boolean) => void;
  selectedCategory: Category;
};
export default function DeleteCategory({
  isFormOpen,
  selectedCategory,
  setIsFormOpen,
}: Props) {
  const { isPending, mutate } = useDeleteCategory({
    onSuccess() {
      setIsFormOpen(false);
    },
  });
  const handleCloseDialog = () => setIsFormOpen(false);
  return (
    <Dialog open={isFormOpen} onOpenChange={setIsFormOpen}>
      <DialogContent className="dir text-right sm:max-w-md">
        <DialogHeader>
          <DialogTitle>تایید حذف دسته (Confirm Delete)</DialogTitle>
        </DialogHeader>
        <DialogDescription>
          آیا از حذف دسته بندی "{selectedCategory?.name}" مطمئن هستید؟ این عمل
          قابل بازگشت نیست. (Are you sure you want to delete the category "
          {selectedCategory.name}"? This action cannot be undone.)
        </DialogDescription>
        <DialogFooter className="mt-4">
          <Button
            variant="outline"
            onClick={handleCloseDialog}
            disabled={isPending}
          >
            لغو (Cancel)
          </Button>
          <Button
            variant="destructive"
            onClick={() => mutate(selectedCategory.id)}
            disabled={isPending}
          >
            {isPending ? "در حال حذف..." : "حذف (Delete)"}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
