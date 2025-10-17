import { useState } from "react";
import { Button } from "@/components/ui/button";
import { PlusIcon } from "lucide-react";
import EditButton from "../_components/edit-button";
import DeleteButton from "../_components/delete-button";
import { PaginationControl } from "@/components/modules/pagination-control";
import { showPersianNumber } from "@/lib/utils";
import { useMyStoreItems } from "@/api/mystore/items/items.hooks";
import { StoreItemDetails } from "@/types";
import UpsertItemDialog from "./UpsertItemDialog";
import DeleteItemDialog from "./DeleteItemDialog";

export default function StoreItemsAdminPage() {
  const [page, setPage] = useState(1);
  const [createOpen, setCreateOpen] = useState(false);
  const [editOpen, setEditOpen] = useState(false);
  const [deleteOpen, setDeleteOpen] = useState(false);
  const [selectedItem, setSelectedItem] = useState<StoreItemDetails | null>(
    null,
  );

  const handleOpenCreate = () => {
    setSelectedItem(null);
    setCreateOpen(true);
  };

  const handleOpenEdit = (item: StoreItemDetails) => {
    setSelectedItem(item);
    setEditOpen(true);
  };

  const handleOpenDelete = (item: StoreItemDetails) => {
    setSelectedItem(item);
    setDeleteOpen(true);
  };
  const { data: storeItemsData, isLoading } = useMyStoreItems({ page });

  return (
    <div className="bg-gray-50 p-4 md:p-6 dark:bg-gray-900">
      <UpsertItemDialog isFormOpen={createOpen} setIsFormOpen={setCreateOpen} />

      {selectedItem && (
        <UpsertItemDialog
          initialData={selectedItem}
          isFormOpen={editOpen}
          setIsFormOpen={setEditOpen}
        />
      )}

      {selectedItem && (
        <DeleteItemDialog
          selectedItem={selectedItem}
          isFormOpen={deleteOpen}
          setIsFormOpen={setDeleteOpen}
        />
      )}

      <div className="mx-auto max-w-7xl">
        <div className="mb-6 flex items-center justify-between">
          <h1 className="text-2xl font-semibold text-gray-800 dark:text-white">
            مدیریت موجودی فروشگاه (Store Items)
          </h1>
          <Button onClick={handleOpenCreate} size="sm">
            <PlusIcon className="mr-2 h-5 w-5" />
            افزودن محصول به فروشگاه
          </Button>
        </div>

        {isLoading && (
          <p className="text-center text-gray-500 dark:text-gray-400">
            در حال بارگذاری...
          </p>
        )}

        {!isLoading && storeItemsData?.results?.length === 0 && (
          <p className="text-center text-gray-500 dark:text-gray-400">
            موردی یافت نشد.
          </p>
        )}

        {!isLoading && storeItemsData && (
          <div className="overflow-x-auto rounded-lg bg-white shadow-md dark:bg-slate-800">
            <table className="min-w-full divide-y divide-gray-200 dark:divide-slate-700">
              <thead className="bg-gray-50 dark:bg-slate-700">
                <tr>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase dark:text-gray-300">
                    نام محصول
                  </th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase dark:text-gray-300">
                    قیمت
                  </th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase dark:text-gray-300">
                    قیمت تخفیف‌خورده
                  </th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase dark:text-gray-300">
                    موجودی
                  </th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase dark:text-gray-300">
                    وضعیت
                  </th>
                  <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase dark:text-gray-300">
                    عملیات
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200 bg-white dark:divide-slate-700 dark:bg-slate-800">
                {storeItemsData.results.map((item) => (
                  <tr
                    key={item.id}
                    className="hover:bg-gray-50 dark:hover:bg-slate-700/50"
                  >
                    <td className="px-6 py-4 text-sm text-gray-900 dark:text-gray-100">
                      {item.product.name}
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-700 dark:text-gray-300">
                      {showPersianNumber(item.price)}
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-700 dark:text-gray-300">
                      {showPersianNumber(item.discount_price)}
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-700 dark:text-gray-300">
                      {showPersianNumber(item.stock)}
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-500 dark:text-gray-400">
                      {item.is_active ? "فعال" : "غیرفعال"}
                    </td>
                    <td className="px-6 py-4 text-center text-sm font-medium whitespace-nowrap">
                      <EditButton onClick={() => handleOpenEdit(item)} />
                      <DeleteButton onClick={() => handleOpenDelete(item)} />
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {storeItemsData && storeItemsData.count > 0 && (
          <PaginationControl
            currentPage={page}
            setCurrentPage={setPage}
            total={storeItemsData.count}
          />
        )}
      </div>
    </div>
  );
}
