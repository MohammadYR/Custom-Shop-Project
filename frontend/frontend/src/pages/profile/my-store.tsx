import { useForm } from "react-hook-form";
import { Button } from "@/components/ui/button";
import { useRegisterStoreMutation } from "@/api/myuser/myuser.hooks";
import { useMyStoreQuery } from "@/api/mystore/strore/store.hooks";
import InputWithLabel from "@/components/ui/input-with-label";

type RegisterStoreForm = {
  name: string;
  description: string;
};

export default function MyStore() {
  const { data: myStore } = useMyStoreQuery();
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<RegisterStoreForm>();

  const {
    mutate: registerStore,
    isPending,
    isError,
  } = useRegisterStoreMutation();

  const onSubmit = (data: RegisterStoreForm) => {
    registerStore(data);
  };

  if (myStore) {
    return (
      <div className="p-4">
        <div className="text-green-700">
          شما صاحب فروشگاه هستید: {myStore.name}
        </div>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-md p-4">
      <div className="mb-4 text-red-700">شما در حال حاضر فروشگاهی ندارید</div>

      {isError && (
        <div className="mb-4 rounded bg-red-200 p-2 text-sm text-red-900">
          خطا در ارسال درخواست
        </div>
      )}

      <form onSubmit={handleSubmit(onSubmit)} className="flex flex-col gap-4">
        <InputWithLabel
          id="name"
          label="نام فروشگاه"
          {...register("name", { required: "نام فروشگاه الزامی است" })}
          error={errors.name?.message}
        />
        <InputWithLabel
          id="description"
          label="توضیحات"
          {...register("description", { required: "توضیحات الزامی است" })}
          error={errors.description?.message}
        />
        <Button type="submit" disabled={isPending}>
          درخواست ثبت فروشگاه
        </Button>
      </form>
    </div>
  );
}
