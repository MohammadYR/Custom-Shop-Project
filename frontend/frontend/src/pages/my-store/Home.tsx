import { useForm } from "react-hook-form";
import InputWithLabel from "@/components/ui/input-with-label";
import { AddressBox } from "../profile/_components/address-box";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  useMyStoreQuery,
  useUpdateMyStoreQuery,
} from "@/api/mystore/strore/store.hooks";
import { Button } from "@/components/ui/button";
import { useEffect } from "react";

type StoreForm = {
  name: string;
  description: string;
};

export default function MyStore() {
  const { data: myStore } = useMyStoreQuery();
  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm<StoreForm>();

  const { mutate: updateStore, isPending } = useUpdateMyStoreQuery();

  // Populate form when data is loaded
  useEffect(() => {
    if (myStore) {
      reset({
        name: myStore.name,
        description: myStore.description,
      });
    }
  }, [myStore, reset]);

  const onSubmit = (data: StoreForm) => {
    updateStore(data);
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle className="mb-6 text-xl">مشخصات فروشگاه</CardTitle>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
          <InputWithLabel
            label="نام"
            {...register("name", { required: "نام فروشگاه الزامی است" })}
            error={errors.name?.message}
          />
          <InputWithLabel
            label="توضیحات"
            {...register("description", {
              required: "توضیحات فروشگاه الزامی است",
            })}
            error={errors.description?.message}
          />
          <Button type="submit" disabled={isPending}>
            بروزرسانی فروشگاه
          </Button>
        </form>

        <div className="mt-6 space-y-4">
          {myStore?.address.map((address) => (
            <AddressBox key={address.id} address={address} />
          ))}
        </div>
      </CardContent>
    </Card>
  );
}
