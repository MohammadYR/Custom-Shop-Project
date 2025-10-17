import { CategoryCombobox } from "@/components/category-combobox";
import InputWithLabel from "@/components/ui/input-with-label";
import { Textarea } from "@/components/ui/textarea";
import { Category } from "@/types";
import React, { RefObject, useRef, useState } from "react";

interface CategoryFormProps {
  initialData?: Category; // for edit mode
  onSubmit: (formData: FormData) => void;
  ref: RefObject<HTMLFormElement | null>;
}

const CategoryForm: React.FC<CategoryFormProps> = ({
  initialData,
  onSubmit,
  ref,
}) => {
  const [name, setName] = useState(initialData?.name || "");
  const [description, setDescription] = useState(
    initialData?.description || "",
  );
  const [isActive, setIsActive] = useState(initialData?.is_active ?? true);
  const [imageFile, setImageFile] = useState<File | null>(null);
  const [selectedCategory, setSelectedCategory] = useState<number | null>(
    initialData ? initialData.parent : null,
  );

  const fileInputRef = useRef<HTMLInputElement | null>(null);

  const handleImageChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setImageFile(file);
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const formData = new FormData();
    if (initialData?.id) {
      formData.append("id", String(initialData.id));
    }
    formData.append("name", name);
    formData.append("description", description);
    formData.append("is_active", String(isActive));
    formData.append("parent", String(selectedCategory));
    if (imageFile) {
      formData.append("image", imageFile);
    }
    onSubmit(formData);
  };

  return (
    <form
      ref={ref}
      onSubmit={handleSubmit}
      className="w-full max-w-md space-y-6 rounded-xl bg-white p-6 shadow-md"
    >
      <div>
        <InputWithLabel
          label="نام"
          type="text"
          value={name}
          onChange={(e) => setName(e.target.value)}
          required
        />
      </div>
      <CategoryCombobox
        value={selectedCategory}
        setValue={setSelectedCategory}
      />
      <div>
        <label htmlFor="description" className="text-sm text-gray-700">
          توضیحات
        </label>
        <Textarea
          id="description"
          value={description}
          onChange={(e) => setDescription(e.target.value)}
        />
      </div>

      <div className="flex items-center space-x-3">
        <input
          type="checkbox"
          checked={isActive}
          onChange={(e) => setIsActive(e.target.checked)}
          id="isActive"
          className="h-4 w-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
        />
        <label htmlFor="isActive" className="text-sm text-gray-700">
          فعال
        </label>
      </div>

      <div>
        <label className="mb-2 block text-sm text-gray-700">آپلود تصویر</label>
        <input
          ref={fileInputRef}
          type="file"
          accept="image/*"
          onChange={handleImageChange}
          className="block w-full text-sm text-gray-500 file:mr-4 file:rounded file:border-0 file:bg-blue-50 file:px-4 file:py-2 file:text-sm file:font-semibold file:text-blue-700 hover:file:bg-blue-100"
        />
        {imageFile && (
          <p className="mt-1 text-xs text-gray-500">
            تصویر انتخاب شده: {imageFile.name}
          </p>
        )}
      </div>
    </form>
  );
};

export default CategoryForm;
