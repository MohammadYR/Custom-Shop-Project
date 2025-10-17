"use client";

import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { useForm } from "react-hook-form";
import { z } from "zod";
import { zodResolver } from "@hookform/resolvers/zod";
import { StoreItemDetails } from "@/types";
import { useEffect } from "react";
import {
  useAddMyStoreItem,
  useUpdateMyStoreItem,
} from "@/api/mystore/items/items.hooks";
import { cn } from "@/lib/utils";

const formSchema = z.object({
  product: z.number().int(),
  price: z.string(),
  discount_price: z.string().optional(),
  stock: z.number().int(),
  is_active: z.boolean(),
});

type FormValues = z.infer<typeof formSchema>;

interface Props {
  isFormOpen: boolean;
  setIsFormOpen: (open: boolean) => void;
  initialData?: StoreItemDetails;
}

export default function UpsertItemDialog({
  isFormOpen,
  setIsFormOpen,
  initialData,
}: Props) {
  const isEdit = !!initialData;

  const {
    register,
    handleSubmit,
    reset,
    watch,
    setValue,
    formState: { errors },
  } = useForm<FormValues>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      product: initialData?.product.id || 0,
      price: initialData?.price || "0",
      discount_price: initialData?.discount_price || "0",
      stock: initialData?.stock || 0,
      is_active: initialData?.is_active ?? true,
    },
  });

  useEffect(() => {
    if (initialData) {
      reset({
        product: initialData.product.id,
        price: initialData.price,
        discount_price: initialData.discount_price,
        stock: initialData.stock,
        is_active: initialData.is_active,
      });
    }
  }, [initialData, reset]);

  const createMutation = useAddMyStoreItem();
  const updateMutation = useUpdateMyStoreItem();

  const onSubmit = (values: FormValues) => {
    const action = isEdit
      ? updateMutation.mutateAsync({
          id: initialData!.id,
          ...values,
        })
      : createMutation.mutateAsync({ ...values });

    action.then(() => {
      setIsFormOpen(false);
      reset();
    });
  };

  return (
    <Dialog open={isFormOpen} onOpenChange={setIsFormOpen}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>
            {isEdit ? "ویرایش آیتم فروشگاه" : "افزودن آیتم جدید"}
          </DialogTitle>
        </DialogHeader>
        <form onSubmit={handleSubmit(onSubmit)} className="mt-4 space-y-4">
          <div className={cn(initialData && "hidden")}>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
              شناسه محصول
            </label>
            <Input
              type="number"
              {...register("product", { valueAsNumber: true })}
            />
            {errors.product && (
              <p className="text-sm text-red-500">{errors.product.message}</p>
            )}
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
              قیمت
            </label>
            <Input type="number" {...register("price")} />
            {errors.price && (
              <p className="text-sm text-red-500">{errors.price.message}</p>
            )}
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
              قیمت تخفیف
            </label>
            <Input {...register("discount_price")} />
            {errors.discount_price && (
              <p className="text-sm text-red-500">
                {errors.discount_price.message}
              </p>
            )}
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
              موجودی
            </label>
            <Input
              type="number"
              {...register("stock", { valueAsNumber: true })}
            />
            {errors.stock && (
              <p className="text-sm text-red-500">{errors.stock.message}</p>
            )}
          </div>
          <div className="flex items-center gap-2">
            <label className="text-sm text-gray-700 dark:text-gray-300">
              <input
                type="checkbox"
                className="inline-block size-4"
                checked={watch("is_active")}
                onChange={(e) => setValue("is_active", e.target.checked)}
              />
              <span className="cursor-pointer p-2">فعال</span>
            </label>
          </div>
          <div className="flex justify-end gap-2">
            <Button
              type="button"
              variant="ghost"
              onClick={() => setIsFormOpen(false)}
            >
              انصراف
            </Button>
            <Button type="submit">{isEdit ? "ذخیره تغییرات" : "ایجاد"}</Button>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  );
}
