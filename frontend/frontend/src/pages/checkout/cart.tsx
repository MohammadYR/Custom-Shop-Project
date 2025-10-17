import Container from "@/components/ui/container";
import { ProductCartItem } from "./_components/product-cart-item";
import { useCart } from "@/api/mycart/mycart.hooks";
import { CartSummery } from "./_components/cart-summery";
import { useNavigate } from "react-router";
import { CartEmptyState } from "./_components/cart-empty-state";
import { useAuth } from "@/hooks/useAuth";
import { useEffect } from "react";

export default function Cart() {
  const { data, isError, isLoading } = useCart();
  const { isLogin } = useAuth();
  const navigate = useNavigate();
  useEffect(() => {
    if (!isLogin) {
      navigate("/");
    }
  }, [isLogin, navigate]);
  if (isLoading) {
    return <div>Loading...</div>;
  }
  if (isError) {
    return <div>Error loading cart</div>;
  }

  return (
    <Container>
      <div className="flex w-full flex-col md:flex-row">
        <div className="grow">
          <div className="border-b pb-1.5">سبد خرید</div>
          {data && data.items.length === 0 && <CartEmptyState />}
          {data?.items.map((item) => (
            <ProductCartItem key={item.id} cartItem={item} />
          ))}
        </div>
        <div>
          <CartSummery onClick={() => navigate("/checkout/shipping")} />
        </div>
      </div>
    </Container>
  );
}
