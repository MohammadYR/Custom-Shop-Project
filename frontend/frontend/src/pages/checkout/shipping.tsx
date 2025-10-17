import { toast } from "sonner";

import { AddressBox } from "../profile/_components/address-box";
import Container from "@/components/ui/container";
import { useEffect, useState } from "react";
import { useOrderMutation } from "@/api/orders/orders.hooks";
import { AddAddress } from "../profile/_components/add-address";
import { CartSummery } from "./_components/cart-summery";
import { useUserAddress } from "@/api/myuser/myuser.hooks";
import { useCartItems } from "@/api/mycart/mycart.hooks";
import { useNavigate } from "react-router";

export default function Shipping() {
  const { data: userAddressList } = useUserAddress();
  const navigate = useNavigate();
  const { data: cardItems } = useCartItems();
  const [selectedAddressId, setSelectedAddressId] = useState<number | null>(
    null,
  );
  const orderMutation = useOrderMutation();
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (selectedAddressId) {
      orderMutation
        .mutateAsync({ address_id: selectedAddressId })
        .then((data) => {
          window.location.href = data.payment_url;
        });
    } else {
      toast.error("آدرس انتخاب نشده است.", {
        description: "برای ارسال سفارش باید یک آدرس انتخاب کنید",
      });
    }
  };
  useEffect(() => {
    if (cardItems && !cardItems.length) {
      navigate("/cart");
    }
  }, [cardItems, navigate]);
  return (
    <Container>
      <form onSubmit={handleSubmit} className="space-y-6">
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <p className="font-semibold">انتخاب محل ارسال</p>
            <AddAddress />
          </div>
          <div className="flex justify-between gap-2">
            <div className="grow space-y-3">
              {userAddressList?.map((address) => (
                <label key={address.id} className="block cursor-pointer">
                  <input
                    type="radio"
                    name="address"
                    value={address.id}
                    checked={selectedAddressId === address.id}
                    onChange={() => setSelectedAddressId(address.id)}
                    className="sr-only"
                  />
                  <AddressBox
                    address={address}
                    isSelected={selectedAddressId === address.id}
                  />
                </label>
              ))}
            </div>

            <CartSummery />
          </div>
        </div>
      </form>
    </Container>
  );
}
