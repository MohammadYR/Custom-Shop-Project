import { Label } from "@radix-ui/react-label";
import { Input } from "./input";
import { cn } from "@/lib/utils";

interface InputWithLabelProps extends React.ComponentProps<"input"> {
  label: string;
  labelProps?: React.ComponentProps<"label">;
  inputClass?: string;
  error?: string;
}
export default function InputWithLabel({
  className,
  label,
  id,
  labelProps,
  inputClass,
  error,
  ...rest
}: InputWithLabelProps) {
  return (
    <div className={cn("flex w-full flex-col items-start gap-2", className)}>
      <Label
        htmlFor={id}
        {...labelProps}
        className={cn(labelProps?.className, "w-full")}
      >
        {label}
        <Input id={id} {...rest} className={cn(inputClass, "mt-1 w-full")} />
      </Label>
      {error && <span className="mt-1 bg-red-200 p-3">{error}</span>}
    </div>
  );
}
