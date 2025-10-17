"use client";

import * as React from "react";
import { Check, ChevronsUpDown } from "lucide-react";

import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import {
  Command,
  CommandEmpty,
  CommandGroup,
  CommandInput,
  CommandItem,
  CommandList,
} from "@/components/ui/command";
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "@/components/ui/popover";
import { useCategories } from "@/api/categories/categories.hooks";

export function CategoryCombobox({
  value,
  setValue,
}: {
  value: number | null;
  setValue: (value: number | null) => void;
}) {
  const [open, setOpen] = React.useState(false);
  const { data: categoriesData } = useCategories({ page_size: 100 });

  const selectedCategory = categoriesData?.results.find(
    (cat) => cat.id === value,
  );

  return (
    <div className="space-y-2">
      <label className="text-sm text-gray-700">دسته‌بندی</label>

      <Popover open={open} onOpenChange={setOpen}>
        <PopoverTrigger asChild>
          <Button
            variant="outline"
            role="combobox"
            aria-expanded={open}
            className="w-full justify-between"
          >
            {selectedCategory ? selectedCategory.name : "انتخاب دسته‌بندی..."}
            <ChevronsUpDown className="ml-2 h-4 w-4 shrink-0 opacity-50" />
          </Button>
        </PopoverTrigger>

        <PopoverContent className="w-[300px] p-0">
          <Command>
            <CommandInput placeholder="جستجوی دسته‌بندی..." />
            <CommandList>
              <CommandEmpty>دسته‌بندی‌ای یافت نشد.</CommandEmpty>
              <CommandGroup>
                {categoriesData?.results.map((category) => (
                  <CommandItem
                    key={category.id}
                    onSelect={() => {
                      setValue(category.id);
                      setOpen(false);
                    }}
                  >
                    <Check
                      className={cn(
                        "mr-2 h-4 w-4",
                        value === category.id ? "opacity-100" : "opacity-0",
                      )}
                    />
                    {category.name}
                  </CommandItem>
                ))}
              </CommandGroup>
            </CommandList>
          </Command>
        </PopoverContent>
      </Popover>
    </div>
  );
}
