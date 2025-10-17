import { useUpdateUserInfo, useUserInfo } from "@/api/myuser/myuser.hooks";
import { Button } from "@/components/ui/button";
import InputWithLabel from "@/components/ui/input-with-label";
import { UserUpdateProfile } from "@/types";
import { useForm } from "react-hook-form";

export default function Profile() {
  const { data: user } = useUserInfo();
  const { register, handleSubmit } = useForm<UserUpdateProfile>();
  const { mutate: update } = useUpdateUserInfo();
  const onSubmit = (data: UserUpdateProfile) => {
    update(data);
  };
  return (
    <div className="rounded-2xl border p-6">
      <form onSubmit={handleSubmit(onSubmit)}>
        <div className="mt-2 mb-4 flex flex-col gap-1.5">
          <InputWithLabel
            defaultValue={user?.email}
            label="ایمیل"
            {...register("email")}
          />
          <InputWithLabel
            defaultValue={user?.first_name}
            label="نام"
            {...register("first_name")}
          />
          <InputWithLabel
            defaultValue={user?.last_name}
            label="نام خانوادگی"
            {...register("last_name")}
          />
          <InputWithLabel
            defaultValue={user?.phone ?? undefined}
            label="موبایل"
            {...register("phone")}
          />
          <Button className="mt-5" type="submit">
            ذخیره
          </Button>
        </div>
      </form>
    </div>
  );
}
