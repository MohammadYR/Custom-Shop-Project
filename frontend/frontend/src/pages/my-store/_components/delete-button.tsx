import { Button } from "@/components/ui/button";
import { TrashIcon } from "lucide-react";

export default function DeleteButton({ onClick }: { onClick: () => void }) {
  return (
    <Button
      variant="ghost"
      size="icon"
      onClick={onClick}
      className="text-red-600 hover:text-red-900 dark:text-red-400 dark:hover:text-red-300"
    >
      <TrashIcon className="h-5 w-5" />
      <span className="sr-only">Delete</span>
    </Button>
  );
}
