import { PaginationControl } from "@/components/modules/pagination-control";
import { Button } from "@/components/ui/button";
import { Category } from "@/types";
import { PlusIcon } from "lucide-react";
import { useState } from "react";
import EditButton from "../_components/edit-button";
import DeleteButton from "../_components/delete-button";
import DeleteCategory from "./delete-dialog";
import UpsertCategoryDialog from "./upsert-category";
import { useAdminCategories } from "@/api/admin/categories/categories.hook";

export default function CategoriesAdminPage() {
  const [page, setPage] = useState(1);
  const { data: categoriesData, isLoading: isLoadingCategories } =
    useAdminCategories({ page });

  const [deleteOpen, setDeleteOpen] = useState(false);
  const [editOpen, setEditOpen] = useState(false);
  const [createOpen, setCreateOpen] = useState(false);
  const [selectedCategory, setSelectedCategory] = useState<Category | null>(
    null,
  ); // For editing

  const handleOpenCreateForm = () => {
    setSelectedCategory(null);
    setCreateOpen(true);
  };

  const handleOpenEditForm = (category: Category) => {
    setSelectedCategory(category);
    setEditOpen(true);
  };
  const handleOpenDeleteDialog = (category: Category) => {
    setSelectedCategory(category);
    setDeleteOpen(true);
  };

  return (
    <div className="min-h-screen bg-gray-50 p-4 md:p-6 dark:bg-gray-900">
      <UpsertCategoryDialog
        isFormOpen={createOpen}
        setIsFormOpen={setCreateOpen}
      />
      {selectedCategory && (
        <DeleteCategory
          selectedCategory={selectedCategory}
          isFormOpen={deleteOpen}
          setIsFormOpen={setDeleteOpen}
        />
      )}
      {selectedCategory && (
        <UpsertCategoryDialog
          initialData={selectedCategory}
          isFormOpen={editOpen}
          setIsFormOpen={setEditOpen}
        />
      )}
      <div className="mx-auto max-w-7xl">
        <div className="mb-6 flex items-center justify-between">
          <h1 className="text-2xl font-semibold text-gray-800 dark:text-white">
            مدیریت دسته بندی ها (Categories)
          </h1>
          <Button onClick={handleOpenCreateForm} size="sm">
            <PlusIcon className="mr-2 h-5 w-5" />
            ایجاد دسته جدید (New Category)
          </Button>
        </div>

        {/* Table */}
        {isLoadingCategories && (
          <p className="text-center text-gray-500 dark:text-gray-400">
            در حال بارگذاری دسته بندی ها...
          </p>
        )}
        {!isLoadingCategories && categoriesData?.results?.length === 0 && (
          <p className="text-center text-gray-500 dark:text-gray-400">
            هیچ دسته بندی یافت نشد.
          </p>
        )}
        {!isLoadingCategories && categoriesData && categoriesData.count > 0 && (
          <div className="overflow-hidden rounded-lg bg-white shadow-md dark:bg-slate-800">
            <table className="min-w-full divide-y divide-gray-200 dark:divide-slate-700">
              <thead className="bg-gray-50 dark:bg-slate-700">
                <tr>
                  <th
                    scope="col"
                    className="px-6 py-3 text-right text-xs font-medium tracking-wider text-gray-500 uppercase dark:text-gray-300"
                  >
                    شناسه (ID)
                  </th>
                  <th
                    scope="col"
                    className="px-6 py-3 text-right text-xs font-medium tracking-wider text-gray-500 uppercase dark:text-gray-300"
                  >
                    نام (Name)
                  </th>
                  <th
                    scope="col"
                    className="px-6 py-3 text-right text-xs font-medium tracking-wider text-gray-500 uppercase dark:text-gray-300"
                  >
                    توضیحات (Description)
                  </th>
                  <th
                    scope="col"
                    className="px-6 py-3 text-center text-xs font-medium tracking-wider text-gray-500 uppercase dark:text-gray-300"
                  >
                    وضعیت (Status)
                  </th>
                  <th
                    scope="col"
                    className="px-6 py-3 text-center text-xs font-medium tracking-wider text-gray-500 uppercase dark:text-gray-300"
                  >
                    عملیات (Actions)
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200 bg-white dark:divide-slate-700 dark:bg-slate-800">
                {categoriesData.results.map((item) => (
                  <tr
                    key={item.id}
                    className="hover:bg-gray-50 dark:hover:bg-slate-700/50"
                  >
                    <td className="px-6 py-4 text-sm font-medium whitespace-nowrap text-gray-900 dark:text-gray-100">
                      {item.id}
                    </td>
                    <td className="px-6 py-4 text-sm whitespace-nowrap text-gray-700 dark:text-gray-300">
                      {item.name}
                    </td>
                    <td
                      className="max-w-xs truncate px-6 py-4 text-sm whitespace-nowrap text-gray-500 dark:text-gray-400"
                      title={item.description}
                    >
                      {item.description}
                    </td>
                    <td className="px-6 py-4 text-center text-sm whitespace-nowrap">
                      {item.is_active ? (
                        <span className="inline-flex rounded-full bg-green-100 px-2 text-xs leading-5 font-semibold text-green-800 dark:bg-green-700 dark:text-green-100">
                          فعال (Active)
                        </span>
                      ) : (
                        <span className="inline-flex rounded-full bg-red-100 px-2 text-xs leading-5 font-semibold text-red-800 dark:bg-red-700 dark:text-red-100">
                          غیرفعال (Inactive)
                        </span>
                      )}
                    </td>
                    <td className="px-6 py-4 text-center text-sm font-medium whitespace-nowrap">
                      <EditButton onClick={() => handleOpenEditForm(item)} />
                      <DeleteButton
                        onClick={() => handleOpenDeleteDialog(item)}
                      />
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {/* Pagination */}
        {categoriesData && categoriesData.count > 0 && (
          <PaginationControl
            currentPage={page}
            setCurrentPage={setPage}
            total={categoriesData.count || 0}
            // pageSize={10} // Assuming your pagination control can take pageSize
          />
        )}
      </div>
    </div>
  );
}
