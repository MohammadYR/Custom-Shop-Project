import { Link } from "react-router";
import { cn } from "@/lib/utils";
type Props = {
  title: string;
  imgSrc: string;
  href: string;
  className?: string;
};
export function CategoryCard({ title, imgSrc, href, className }: Props) {
  return (
    <Link
      to={href}
      className={cn("inline-block rounded-xl border-2", className)}
    >
      <div className="p-1">
        <img
          className="mx-auto size-22 overflow-hidden rounded-lg"
          src={imgSrc}
          alt={`category ${title}`}
        />
      </div>
      <div className="p-1 text-center">{title}</div>
    </Link>
  );
}
