import { useUserDeleteAddress } from "@/api/myuser/myuser.hooks";
import {
  AlertDialog,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogTitle,
} from "@/components/ui/alert-dialog";
import { Button } from "@/components/ui/button";

import { Dispatch, ReactNode, SetStateAction, useRef, useState } from "react";

type DeleteAddressProps = {
  id: string | number;
  renderButton?: (setOpen: Dispatch<SetStateAction<boolean>>) => ReactNode;
};
export function DeleteAddress({ id, renderButton }: DeleteAddressProps) {
  const [open, setOpen] = useState(false);

  const formRef = useRef<HTMLFormElement>(null);
  const { mutate, isPending } = useUserDeleteAddress();
  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    try {
      await mutate(id);
      setOpen(false);
    } catch (err) {
      console.log(err);
    }
  };
  return (
    <>
      {renderButton?.(setOpen)}
      <AlertDialog open={open} onOpenChange={setOpen}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle className="text-right">حذف آدرس</AlertDialogTitle>
            <form ref={formRef} onSubmit={handleSubmit}>
              <AlertDialogDescription className="text-right">
                آیا از حذف آدرس مطمئن هستید؟
              </AlertDialogDescription>
            </form>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel onClick={() => setOpen(false)}>
              انصراف
            </AlertDialogCancel>
            <Button
              type="submit"
              disabled={isPending}
              onClick={() => {
                if (formRef.current) {
                  formRef.current.requestSubmit();
                }
              }}
            >
              حذف
            </Button>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </>
  );
}
