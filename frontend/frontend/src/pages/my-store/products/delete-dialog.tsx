import { useDeleteProduct } from "@/api/products/products.hooks";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Product } from "@/types";

type Props = {
  isFormOpen: boolean;
  setIsFormOpen: (open: boolean) => void;
  selectedProduct: Product;
};

export default function DeleteProduct({
  isFormOpen,
  selectedProduct,
  setIsFormOpen,
}: Props) {
  const { isPending, mutate } = useDeleteProduct({
    onSuccess() {
      setIsFormOpen(false);
    },
  });

  const handleCloseDialog = () => setIsFormOpen(false);

  return (
    <Dialog open={isFormOpen} onOpenChange={setIsFormOpen}>
      <DialogContent className="dir text-right sm:max-w-md">
        <DialogHeader>
          <DialogTitle>تایید حذف محصول (Confirm Delete)</DialogTitle>
        </DialogHeader>
        <DialogDescription>
          آیا از حذف محصول "{selectedProduct?.name}" مطمئن هستید؟ این عمل قابل
          بازگشت نیست. (Are you sure you want to delete the product "
          {selectedProduct.name}"? This action cannot be undone.)
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
            onClick={() => mutate(selectedProduct.id)}
            disabled={isPending}
          >
            {isPending ? "در حال حذف..." : "حذف (Delete)"}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
