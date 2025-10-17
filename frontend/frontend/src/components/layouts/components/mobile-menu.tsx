import { OutlineMenuIcon } from "@/icons/outline-menu";
import { Sheet, SheetContent, SheetTrigger } from "@/components/ui/sheet";
import { Button } from "@/components/ui/button";
import { useCategories } from "@/api/categories/categories.hooks";
export default function MobileMenu() {
  const { data: categories } = useCategories();
  return (
    <div className="md:hidden">
      <Sheet>
        <SheetTrigger asChild>
          <Button variant="ghost" size="icon">
            <OutlineMenuIcon className="size-6" />
          </Button>
        </SheetTrigger>
        <SheetContent side="right">
          <nav className="flex flex-col gap-5 p-4">
            <a href="/" className="text-lg font-medium">
              خانه
            </a>
            {categories?.results.map((item) => (
              <a
                key={item.id}
                href={`/${item.id}`}
                className="text-lg font-medium"
              >
                {item.name}
              </a>
            ))}

            <a href="/about" className="text-lg font-medium">
              درباره ما
            </a>
          </nav>
        </SheetContent>
      </Sheet>
    </div>
  );
}
