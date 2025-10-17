import { Button } from "@/components/ui/button";
import { Filter, ListFilter } from "lucide-react";
import { ProductCard } from "@/components/product-card";
import FilterForm from "@/components/modules/FilterForm";
import Container from "@/components/ui/container";
import { useParams } from "react-router";
import { useGetCategory } from "@/api/categories/categories.hooks";
import { useSiteTitle } from "@/hooks/useSiteTitle";
import { useEffect, useState } from "react";
import { PaginationControl } from "@/components/modules/pagination-control";
import { ProductsQueryFilter } from "@/types";
import { useProducts } from "@/api/products/products.hooks";

export default function Category() {
  const { categoryId } = useParams();
  const [params, setParams] = useState<Partial<ProductsQueryFilter>>();
  const handleSort = (ordering: ProductsQueryFilter["ordering"]) => {
    setParams((prev) => ({ ...prev, ordering }));
  };
  const { data: category } = useGetCategory(categoryId!);
  useSiteTitle(category?.name);
  const { data: products } = useProducts(params);
  useEffect(() => {
    if (category) {
      setParams({ category: category?.id.toString() });
    }
  }, [category]);
  return (
    <Container>
      <div className="flex flex-col md:flex-row">
        <div className="bg-background sticky top-[72px] flex gap-2 border-b border-gray-300 shadow md:hidden">
          <Button variant={"ghost"}>
            <Filter />
            فیلتر
          </Button>
          <Button variant={"ghost"}>
            <ListFilter />
            پربازدیدترین
          </Button>
        </div>
        <div className="relative hidden w-[300px] shrink-0 p-2 md:block">
          <div className="sticky top-[185px]">
            <FilterForm query={params} setQuery={setParams} />
          </div>
        </div>
        <div className="w-full grow p-2">
          <div className="hidden md:block">
            <ul className="m-2 mt-0 flex flex-row items-center gap-3 text-sm">
              <li>
                <a href="#" onClick={() => handleSort("rating")}>
                  پیشنهاد خریداران
                </a>
              </li>
              <li>
                <a href="#" onClick={() => handleSort("-created_at")}>
                  جدیدترین
                </a>
              </li>
              <li>
                <a href="#" onClick={() => handleSort("-price")}>
                  گران ترین
                </a>
              </li>
              <li>
                <a href="#" onClick={() => handleSort("price")}>
                  ارزان ترین
                </a>
              </li>
            </ul>
          </div>
          <div className="grid grow grid-cols-2 gap-2 p-2 md:grid-cols-3">
            {products?.results.map((item) => (
              <ProductCard
                key={item.id}
                id={item.id.toString()}
                image={item.images[0]?.image}
                best_seller={item.best_seller}
                name={item.name}
              />
            ))}
          </div>
          <PaginationControl
            currentPage={params?.page || 1}
            setCurrentPage={(newPage) =>
              setParams((oldParams) => ({ ...oldParams, page: newPage }))
            }
            total={products?.count}
          />
        </div>
      </div>
    </Container>
  );
}
