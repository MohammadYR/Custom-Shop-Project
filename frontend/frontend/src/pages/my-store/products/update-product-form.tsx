import { useForm, Controller } from "react-hook-form";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { Checkbox } from "@/components/ui/checkbox";
import { Textarea } from "@/components/ui/textarea";
import { useEffect, useState } from "react";
import { Product } from "@/types";
import { useUpdateProduct } from "@/api/products/products.hooks";
import { DialogFooter } from "@/components/ui/dialog";
import { CategoryCombobox } from "@/components/category-combobox";

type EditProductFormProps = {
  product: Product;
  handleCloseDialog: () => void;
};

type FormValues = {
  name: string;
  description: string;
  is_active: boolean;
  categories: number[];
  images: FileList;
};

export default function EditProductForm({
  product,
  handleCloseDialog,
}: EditProductFormProps) {
  const [selectedCategory, setSelectedCategory] = useState<number | null>(null);

  const { register, handleSubmit, control, reset } = useForm<FormValues>();

  useEffect(() => {
    if (product) {
      reset({
        name: product.name,
        description: product.description,
        is_active: product.is_active,
      });
      setSelectedCategory(product.category.id);
    }
  }, [product, reset]);

  const mutation = useUpdateProduct(product.id, {
    onSuccess: () => {
      handleCloseDialog();
    },
  });

  const onSubmit = (data: FormValues) => {
    const formData = new FormData();
    formData.append("name", data.name);
    formData.append("description", data.description);
    formData.append("is_active", String(data.is_active || true));
    formData.append("category", String(selectedCategory));

    if (data.images && data.images.length > 0) {
      Array.from(data.images).forEach((file) => {
        formData.append("images", file);
      });
    }

    mutation.mutate(formData);
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
      <div>
        <Label className="mb-2">نام محصول</Label>
        <Input {...register("name", { required: true })} />
      </div>

      <div>
        <Label className="mb-2">توضیحات</Label>
        <Textarea {...register("description", { required: true })} />
      </div>

      <div>
        <Label htmlFor="is_active" className="inline p-2">
          فعال باشد؟
        </Label>
        <Controller
          name="is_active"
          control={control}
          defaultValue={true}
          render={({ field }) => (
            <Checkbox
              id="is_active"
              checked={field.value}
              onCheckedChange={field.onChange}
            />
          )}
        />
      </div>

      <div>
        <CategoryCombobox
          value={selectedCategory}
          setValue={setSelectedCategory}
        />
      </div>

      <div>
        <Label>تصاویر جدید (در صورت نیاز)</Label>
        <Input type="file" multiple {...register("images")} />
      </div>

      <DialogFooter className="mt-4">
        <Button variant="outline" onClick={handleCloseDialog}>
          لغو (Cancel)
        </Button>
        <Button type="submit" disabled={mutation.isPending}>
          {mutation.isPending ? "در حال ارسال..." : "ذخیره تغییرات"}
        </Button>
      </DialogFooter>
    </form>
  );
}
