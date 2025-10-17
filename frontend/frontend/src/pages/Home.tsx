import { ScrollSection } from "@/components/scroll-section";
import { CategoryCard } from "@/components/category-card";
import { OfferSection } from "@/components/offer-section";
import { ProductCard } from "@/components/product-card";
import Container from "@/components/ui/container";
import { useCategories } from "@/api/categories/categories.hooks";
import { useProducts } from "@/api/products/products.hooks";

export default function Home() {
  const { data: categories } = useCategories();
  const { data: products } = useProducts();
  return (
    <main className="mb-2 md:mb-14">
      <Container>
        <OfferSection title="محصولات پیشنهادی">
          {products?.results.map((item, index) => (
            <ProductCard
              key={item.id}
              className={index >= 4 ? "hidden md:block" : "block"}
              id={item.id.toString()}
              image={item.images[0]?.image}
              best_seller={item.best_seller}
              name={item.name}
            />
          ))}
        </OfferSection>
        <ScrollSection title="دسته بندی محصولات" className="mt-8">
          {categories?.results.map((item) => (
            <CategoryCard
              key={item.id}
              title={item.name}
              href={`/categories/${item.id}`}
              imgSrc={item.image}
            />
          ))}
        </ScrollSection>
        <OfferSection title="طرح های پرطرفدار" className="mt-6">
          {products?.results.map((item, index) => (
            <ProductCard
              key={item.id}
              className={index >= 4 ? "hidden md:block" : "block"}
              id={item.id.toString()}
              image={item.images[0]?.image}
              best_seller={item.best_seller}
              name={item.name}
            />
          ))}
        </OfferSection>
      </Container>
    </main>
  );
}
