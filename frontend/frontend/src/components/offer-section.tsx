import { ReactNode } from "react";
import { Button } from "./ui/button";

type Props = {
  title: string;
  children: ReactNode;
  className?: string;
};
export function OfferSection({ title, children, className }: Props) {
  return (
    <section className={className}>
      <div className="mb-2 flex items-center justify-between">
        <div className="text-md font-semibold">{title}</div>
        <Button variant="link">مشاهده همه</Button>
      </div>
      <div className="grid grid-cols-2 gap-2 md:grid-cols-4 md:gap-4">
        {children}
      </div>
    </section>
  );
}
