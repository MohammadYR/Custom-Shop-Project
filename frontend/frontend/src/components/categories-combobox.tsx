"use client";

import * as React from "react";
import { Check, ChevronsUpDown, X } from "lucide-react";

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

export function CategoriesCombobox({
  value,
  setValue,
}: {
  value: number[];
  setValue: (values: number[]) => void;
}) {
  const [open, setOpen] = React.useState(false);
  const { data: categoriesData } = useCategories({ page_size: 100 });

  const toggleCategory = (id: number) => {
    setValue(
      value.includes(id) ? value.filter((v) => v !== id) : [...value, id],
    );
  };

  const selectedCategories =
    categoriesData?.results.filter((cat) => value.includes(cat.id)) || [];

  return (
    <div className="space-y-2">
      <label className="text-sm text-gray-700">دسته‌بندی‌ها</label>

      <Popover open={open} onOpenChange={setOpen}>
        <PopoverTrigger asChild>
          <Button
            variant="outline"
            role="combobox"
            aria-expanded={open}
            className="w-full justify-between"
          >
            {value.length > 0
              ? `${value.length} دسته‌بندی انتخاب شده`
              : "انتخاب دسته‌بندی..."}
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
                    onSelect={() => toggleCategory(category.id)}
                  >
                    <Check
                      className={cn(
                        "mr-2 h-4 w-4",
                        value.includes(category.id)
                          ? "opacity-100"
                          : "opacity-0",
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

      {selectedCategories.length > 0 && (
        <div className="flex flex-wrap gap-2">
          {selectedCategories.map((cat) => (
            <div
              key={cat.id}
              className="flex items-center rounded-full bg-blue-100 px-3 py-1 text-sm text-blue-800"
            >
              {cat.name}
              <button
                onClick={() => toggleCategory(cat.id)}
                className="ml-2 text-blue-500 hover:text-blue-700"
              >
                <X className="h-4 w-4" />
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
