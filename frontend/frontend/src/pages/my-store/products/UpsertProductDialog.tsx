import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Product } from "@/types";
import ProductForm from "./product-form";
import EditProductForm from "./update-product-form";

type Props = {
  isFormOpen: boolean;
  setIsFormOpen: (open: boolean) => void;
  initialData?: Product;
};

export default function UpsertProductDialog({
  isFormOpen,
  setIsFormOpen,
  initialData,
}: Props) {
  const handleCloseDialog = () => setIsFormOpen(false);

  return (
    <Dialog modal={false} open={isFormOpen} onOpenChange={setIsFormOpen}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>
            {initialData
              ? "ویرایش محصول (Edit Product)"
              : "ایجاد محصول جدید (Create New Product)"}
          </DialogTitle>
          {initialData && (
            <DialogDescription>شناسه محصول: {initialData.id}</DialogDescription>
          )}
        </DialogHeader>
        {initialData ? (
          <EditProductForm
            handleCloseDialog={handleCloseDialog}
            product={initialData}
          />
        ) : (
          <ProductForm handleCloseDialog={handleCloseDialog} />
        )}
      </DialogContent>
    </Dialog>
  );
}
