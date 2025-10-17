import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { StoreItemDetails } from "@/types";
import { useDeleteMyStoreItem } from "@/api/mystore/items/items.hooks";

interface Props {
  selectedItem: StoreItemDetails;
  isFormOpen: boolean;
  setIsFormOpen: (open: boolean) => void;
}

export default function DeleteItemDialog({
  selectedItem,
  isFormOpen,
  setIsFormOpen,
}: Props) {
  const deleteMutation = useDeleteMyStoreItem();

  const handleDelete = async () => {
    await deleteMutation.mutateAsync(selectedItem.id);
    setIsFormOpen(false);
  };

  return (
    <Dialog open={isFormOpen} onOpenChange={setIsFormOpen}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>حذف آیتم</DialogTitle>
        </DialogHeader>
        <p className="text-sm text-gray-700 dark:text-gray-300">
          آیا از حذف آیتم «{selectedItem.product.name}» اطمینان دارید؟
        </p>
        <div className="mt-4 flex justify-end gap-2">
          <Button variant="ghost" onClick={() => setIsFormOpen(false)}>
            انصراف
          </Button>
          <Button variant="destructive" onClick={handleDelete}>
            حذف
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  );
}
