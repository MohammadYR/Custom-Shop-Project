import Container from "@/components/ui/container";
import { Link } from "react-router";
import useScrollTrigger from "@/hooks/useScrollTrigger";
import { cn } from "@/lib/utils";
import { useCategories } from "@/api/categories/categories.hooks";

export function HeaderCategories() {
  const { data: categories } = useCategories();
  const isScrollDown = useScrollTrigger({
    threshold: 100,
  });
  return (
    <section
      className={cn(
        "absolute top-22 right-0 left-0 -z-10 hidden max-h-12 bg-white transition-all duration-300 md:block",
        isScrollDown && "-top-6 overflow-hidden bg-transparent",
      )}
    >
      <Container>
        <div className="flex justify-around py-4">
          {categories?.results?.map((item) => (
            <div key={item.id}>
              <Link to={"/categories/" + item.id}>{item.name}</Link>
            </div>
          ))}
        </div>
      </Container>
    </section>
  );
}
