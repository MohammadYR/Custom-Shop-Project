import {
  Dialog,
  DialogTrigger,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import {
  Select,
  SelectTrigger,
  SelectValue,
  SelectContent,
  SelectItem,
} from "@/components/ui/select";
import { useState } from "react";
import { ShopOrder, OrderStatusDescriptionMap } from "@/types";
import { useChangeOrderStatus } from "@/api/mystore/orders/hooks";

type Props = {
  order: ShopOrder;
};

export function ChangeOrderStatusDialog({ order }: Props) {
  const [newStatus, setNewStatus] = useState<string | null>(
    order.status.toString(),
  );
  const changeStatusMutation = useChangeOrderStatus();

  const handleSubmit = () => {
    if (!newStatus) return;

    changeStatusMutation.mutate({
      id: order.id,
      status: Number(newStatus),
    });

    setNewStatus(null);
  };

  return (
    <Dialog>
      <DialogTrigger asChild>
        <Button variant="outline" size="sm">
          تغییر وضعیت
        </Button>
      </DialogTrigger>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>تغییر وضعیت سفارش #{order.id}</DialogTitle>
        </DialogHeader>

        <Select
          value={newStatus ?? order.status.toString()}
          onValueChange={(val) => setNewStatus(val)}
        >
          <SelectTrigger>
            <SelectValue placeholder="انتخاب وضعیت جدید" />
          </SelectTrigger>
          <SelectContent>
            {Object.entries(OrderStatusDescriptionMap).map(([key, label]) => (
              <SelectItem key={key} value={key}>
                {label}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>

        <DialogFooter>
          <Button
            onClick={handleSubmit}
            disabled={!newStatus || changeStatusMutation.isPending}
          >
            {changeStatusMutation.isPending ? "در حال تغییر..." : "تأیید"}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
