import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import { AddressType } from "@/types";

import { Edit, EllipsisVerticalIcon, MapPin, Trash2 } from "lucide-react";
import { useState } from "react";
import { DeleteAddress } from "./delete-address";
import { AddAddress } from "./add-address";

export function AddressBox({
  address,
  isSelected,
  showOption = false,
}: {
  address: AddressType;
  isSelected?: boolean;
  showOption?: boolean;
}) {
  const [open, setOpen] = useState(false);
  return (
    <>
      <li
        className={cn(
          "relative flex gap-1.5 rounded-2xl border p-4",
          isSelected && "border-blue-400 shadow-lg",
        )}
      >
        <div className="mt-1">
          <MapPin />
        </div>
        <div
          className={cn(
            "absolute top-3 left-3 flex overflow-hidden",
            !showOption && "hidden",
          )}
        >
          <span
            className={cn(
              "inline-flex flex-nowrap transition-all",
              !open && "w-0",
              open && "w-[90px]",
            )}
          >
            <DeleteAddress
              id={address.id}
              renderButton={(setOpen) => (
                <Button
                  type="button"
                  variant={"outline"}
                  size={"icon"}
                  onClick={() => setOpen(true)}
                  className="mx-2"
                >
                  <Trash2 />
                </Button>
              )}
            />
            <AddAddress
              initialAddress={address}
              renderButton={(setOpen) => (
                <Button
                  type="button"
                  variant={"outline"}
                  size={"icon"}
                  onClick={() => setOpen(true)}
                >
                  <Edit className="inline" />
                </Button>
              )}
            />
          </span>
          <div>
            <Button
              type="button"
              onClick={() => setOpen((old) => !old)}
              variant={"outline"}
              size={"icon"}
              className="mx-2"
            >
              <EllipsisVerticalIcon />
            </Button>
          </div>
        </div>

        <div>
          <p>{address.label}</p>
          <p>استان: {address.state}</p>
          <p>شهر: {address.city}</p>
          <p>
            آدرس:{" "}
            {address.address_line_1 +
              " " +
              address.address_line_2 +
              " کدپستی: " +
              address.postal_code}
          </p>
        </div>
      </li>
    </>
  );
}
