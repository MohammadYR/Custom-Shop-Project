import { ReactNode } from "react";

type Props = {
  children?: ReactNode;
  title: string;
  className?: string;
};
export function ScrollSection({ children, title, className }: Props) {
  return (
    <div className={className}>
      <div className="my-3">
        <div className="text-md font-semibold">{title}</div>
      </div>
      <div className="flex flex-nowrap gap-2 overflow-x-scroll p-2 *:shrink-0 md:justify-between md:overflow-x-auto">
        {children}
      </div>
    </div>
  );
}
