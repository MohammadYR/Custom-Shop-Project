import { useState } from "react";
import { Product } from "@/types";
import { Button } from "@/components/ui/button";
import { PlusIcon } from "lucide-react";
import EditButton from "../_components/edit-button";
import DeleteButton from "../_components/delete-button";
// import UpsertProductDialog from "./upsert-product";
import DeleteProductDialog from "./delete-dialog";
import { PaginationControl } from "@/components/modules/pagination-control";
import { showPersianNumber } from "@/lib/utils";
import UpsertProductDialog from "./UpsertProductDialog";
import { useProducts } from "@/api/products/products.hooks";

export default function ProductsAdminPage() {
  const [page, setPage] = useState(1);
  const { data: productsData, isLoading: isLoadingProducts } = useProducts({
    page,
  });

  const [createOpen, setCreateOpen] = useState(false);
  const [editOpen, setEditOpen] = useState(false);
  const [deleteOpen, setDeleteOpen] = useState(false);
  const [selectedProduct, setSelectedProduct] = useState<Product | null>(null);

  const handleOpenCreate = () => {
    setSelectedProduct(null);
    setCreateOpen(true);
  };

  const handleOpenEdit = (product: Product) => {
    setSelectedProduct(product);
    setEditOpen(true);
  };

  const handleOpenDelete = (product: Product) => {
    setSelectedProduct(product);
    setDeleteOpen(true);
  };

  return (
    <div className="bg-gray-50 p-4 md:p-6 dark:bg-gray-900">
      <UpsertProductDialog
        isFormOpen={createOpen}
        setIsFormOpen={setCreateOpen}
      />
      {selectedProduct && (
        <UpsertProductDialog
          initialData={selectedProduct}
          isFormOpen={editOpen}
          setIsFormOpen={setEditOpen}
        />
      )}

      {selectedProduct && (
        <DeleteProductDialog
          selectedProduct={selectedProduct}
          isFormOpen={deleteOpen}
          setIsFormOpen={setDeleteOpen}
        />
      )}

      <div className="mx-auto max-w-7xl">
        <div className="mb-6 flex items-center justify-between">
          <h1 className="text-2xl font-semibold text-gray-800 dark:text-white">
            مدیریت محصولات (Products)
          </h1>
          <Button onClick={handleOpenCreate} size="sm">
            <PlusIcon className="mr-2 h-5 w-5" />
            ایجاد محصول جدید (New Product)
          </Button>
        </div>

        {isLoadingProducts && (
          <p className="text-center text-gray-500 dark:text-gray-400">
            در حال بارگذاری...
          </p>
        )}
        {!isLoadingProducts && productsData?.results?.length === 0 && (
          <p className="text-center text-gray-500 dark:text-gray-400">
            محصولی یافت نشد.
          </p>
        )}

        {!isLoadingProducts && productsData && (
          <div className="overflow-x-auto rounded-lg bg-white shadow-md dark:bg-slate-800">
            <table className="min-w-full divide-y divide-gray-200 dark:divide-slate-700">
              <thead className="bg-gray-50 dark:bg-slate-700">
                <tr>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase dark:text-gray-300">
                    شناسه (ID)
                  </th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase dark:text-gray-300">
                    نام (Name)
                  </th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase dark:text-gray-300">
                    موجودی (Stock)
                  </th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase dark:text-gray-300">
                    قیمت (Price)
                  </th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase dark:text-gray-300">
                    امتیاز (Rating)
                  </th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase dark:text-gray-300">
                    دسته بندی ها (Categories)
                  </th>
                  <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase dark:text-gray-300">
                    عملیات (Actions)
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200 bg-white dark:divide-slate-700 dark:bg-slate-800">
                {productsData.results.map((product) => (
                  <tr
                    key={product.id}
                    className="hover:bg-gray-50 dark:hover:bg-slate-700/50"
                  >
                    <td className="px-6 py-4 text-sm text-gray-900 dark:text-gray-100">
                      {product.id}
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-700 dark:text-gray-300">
                      {product.name}
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-700 dark:text-gray-300">
                      {showPersianNumber(product.stock)}
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-700 dark:text-gray-300">
                      {showPersianNumber(product.best_price ?? 0)}
                    </td>
                    <td className="px-6 py-4 text-sm text-yellow-500 dark:text-yellow-300">
                      {showPersianNumber(product.rating)}
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-500 dark:text-gray-400">
                      {product.category.name}
                    </td>
                    <td className="px-6 py-4 text-center text-sm font-medium whitespace-nowrap">
                      <EditButton onClick={() => handleOpenEdit(product)} />
                      <DeleteButton onClick={() => handleOpenDelete(product)} />
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {/* Pagination */}
        {productsData && productsData.next && (
          <PaginationControl
            currentPage={page}
            setCurrentPage={setPage}
            total={productsData.count}
            // pageSize={10}
          />
        )}
      </div>
    </div>
  );
}
