import {
  AlertDialog,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "@/components/ui/alert-dialog";

import { useForm } from "react-hook-form";
import { Button } from "@/components/ui/button";
import { Dispatch, ReactNode, SetStateAction, useState } from "react";
import { AddressCreateData, AddressType } from "@/types";
import InputWithLabel from "@/components/ui/input-with-label";
import {
  useUserCreateAddress,
  useUserUpdateAddress,
} from "@/api/myuser/myuser.hooks";

type AddAddressProps = {
  initialAddress?: AddressType;
  renderButton?: (setOpen: Dispatch<SetStateAction<boolean>>) => ReactNode;
};
export function AddAddress({ initialAddress, renderButton }: AddAddressProps) {
  const {
    register,
    handleSubmit,
    formState: { isSubmitting },
  } = useForm<AddressCreateData>();
  const { mutateAsync: addAddress } = useUserCreateAddress();
  const { mutateAsync: updateAddress } = useUserUpdateAddress();
  const [open, setOpen] = useState(false);
  const onSubmit = (data: AddressCreateData) => {
    if (initialAddress) {
      updateAddress({
        id: initialAddress.id,
        ...data,
        country: "iran",
      }).then(() => {
        setOpen(false);
      });
      return;
    }
    addAddress({
      ...data,
      country: "iran",
    }).then(() => {
      setOpen(false);
    });
  };

  return (
    <>
      {renderButton?.(setOpen)}
      <AlertDialog open={open}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>اضافه کردن آدرس جدید</AlertDialogTitle>
          </AlertDialogHeader>
          <form onSubmit={handleSubmit(onSubmit)}>
            <AlertDialogDescription>
              <div className="mt-2 mb-4 flex flex-col gap-1.5">
                <InputWithLabel
                  defaultValue={initialAddress?.label}
                  label="برچسب"
                  {...register("label")}
                />
                <InputWithLabel
                  defaultValue={initialAddress?.state}
                  label="استان"
                  {...register("state")}
                />
                <InputWithLabel
                  defaultValue={initialAddress?.city}
                  label="شهر"
                  {...register("city")}
                />
                <InputWithLabel
                  defaultValue={initialAddress?.address_line_1}
                  label="خیابان اصلی"
                  {...register("address_line_1")}
                />
                <InputWithLabel
                  defaultValue={initialAddress?.address_line_2}
                  label="کوچه"
                  {...register("address_line_2")}
                />
                <InputWithLabel
                  defaultValue={initialAddress?.postal_code}
                  label="کدپستی"
                  {...register("postal_code")}
                />
              </div>
            </AlertDialogDescription>
            <AlertDialogFooter>
              <AlertDialogCancel onClick={() => setOpen(false)}>
                انصراف
              </AlertDialogCancel>
              <Button type="submit" disabled={isSubmitting}>
                ثبت آدرس
              </Button>
            </AlertDialogFooter>
          </form>
        </AlertDialogContent>
      </AlertDialog>
    </>
  );
}
