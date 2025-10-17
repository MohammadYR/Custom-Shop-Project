import Container from "@/components/ui/container";
import { useSiteTitle } from "@/hooks/useSiteTitle";
import { useParams } from "react-router";
import { ProductImage } from "./_components/product-image";
import { ProductOverview } from "./_components/product-overview";
import { useGetProduct } from "@/api/products/products.hooks";
import React, { lazy } from "react";
import withSuspense from "@/components/withSuspend";
import {
  Breadcrumb,
  BreadcrumbItem,
  BreadcrumbLink,
  BreadcrumbList,
  BreadcrumbSeparator,
  BreadcrumbPage,
} from "@/components/ui/breadcrumb";

const ShopCard = withSuspense(lazy(() => import("./_components/shop-card")));
const CommentsSection = withSuspense(
  lazy(() => import("./_components/comments-section")),
);
const SellersSection = withSuspense(
  lazy(() => import("./_components/sellers-section")),
);

export default function Product() {
  const { productId } = useParams();
  const { data: product } = useGetProduct(productId!);
  useSiteTitle(product?.name);
  if (!product) {
    return null;
  }
  return (
    <Container>
      <Breadcrumb>
        <BreadcrumbList>
          <BreadcrumbItem>
            <BreadcrumbLink href="/">فروشگاه کاستومی</BreadcrumbLink>
          </BreadcrumbItem>
          <BreadcrumbSeparator />
          {product.category?.parents?.map((parent) => (
            <React.Fragment key={parent.id}>
              <BreadcrumbItem>
                <BreadcrumbLink href={`/categories/${parent.id}`}>
                  {parent.name}
                </BreadcrumbLink>
              </BreadcrumbItem>
              <BreadcrumbSeparator />
            </React.Fragment>
          ))}
          <BreadcrumbItem>
            <BreadcrumbPage>{product.category.name}</BreadcrumbPage>
          </BreadcrumbItem>
        </BreadcrumbList>
      </Breadcrumb>
      <div className="flex flex-col md:flex-row md:items-start md:gap-2">
        <ProductImage product={product} />
        <ProductOverview product={product} />
        <ShopCard product={product} />
      </div>
      <SellersSection sellers={product.sellers} />
      <hr className="my-8" />
      <CommentsSection product={product} />
    </Container>
  );
}
