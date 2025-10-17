import { useForm, Controller } from "react-hook-form";
import { useState } from "react";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { Checkbox } from "@/components/ui/checkbox";
import { Textarea } from "@/components/ui/textarea";
import { useCreateProduct } from "@/api/products/products.hooks";
import { DialogFooter } from "@/components/ui/dialog";
import { CategoryCombobox } from "@/components/category-combobox";

type FormValues = {
  name: string;
  description: string;
  is_active: boolean;
  categories: number[];
  images: FileList;
};

export default function CreateProductForm({
  handleCloseDialog,
}: {
  handleCloseDialog: () => void;
}) {
  const { register, handleSubmit, control, reset } = useForm<FormValues>();
  const [selectedCategory, setSelectedCategory] = useState<number | null>(null);

  const { mutate: createProduct, isPending } = useCreateProduct({
    onSuccess() {
      reset();
      handleCloseDialog();
    },
  });

  const onSubmit = (data: FormValues) => {
    const formData = new FormData();
    formData.append("name", data.name);
    formData.append("description", data.description);
    formData.append("is_active", String(data.is_active));
    formData.append("category", String(selectedCategory));

    Array.from(data.images).forEach((file) => {
      formData.append("images", file);
    });
    createProduct(formData);
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
        <Label className="inline p-2" htmlFor="is_active">
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
        <Label htmlFor="images">تصاویر محصول</Label>
        <Controller
          name="images"
          control={control}
          render={({ field }) => (
            <Input
              id="images"
              type="file"
              multiple
              onChange={(e) => field.onChange(e.target.files)}
            />
          )}
        />
      </div>

      <DialogFooter className="mt-4">
        <Button variant="outline" onClick={handleCloseDialog}>
          لغو (Cancel)
        </Button>
        <Button type="submit" disabled={isPending}>
          {isPending ? "در حال ثبت..." : "ثبت (Save)"}
        </Button>
      </DialogFooter>
    </form>
  );
}
