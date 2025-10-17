import { Button } from "@/components/ui/button";
import { PencilIcon } from "lucide-react";

export default function EditButton({ onClick }: { onClick: () => void }) {
  return (
    <Button
      variant="ghost"
      size="icon"
      onClick={onClick}
      className="mr-2 text-indigo-600 hover:text-indigo-900 dark:text-indigo-400 dark:hover:text-indigo-300"
    >
      <PencilIcon className="h-5 w-5" />
      <span className="sr-only">Edit</span>
    </Button>
  );
}
