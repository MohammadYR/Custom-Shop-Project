import { cn } from "@/lib/utils";

export type ContainerProps = React.ComponentProps<"div">;
export default function Container({ className, ...props }: ContainerProps) {
  return <div className={cn("container mx-auto px-2", className)} {...props} />;
}
