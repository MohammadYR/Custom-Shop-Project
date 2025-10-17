import { MobileLogoIcon } from "@/icons/mobile-logo";
import { DesktopLogoIcon } from "@/icons/desktop-logo";
import MobileMenu from "./mobile-menu";
import { Link } from "react-router";
import { Button } from "../../ui/button";
import { ShoppingCart, User } from "lucide-react";
import Container from "../../ui/container";
import { useAuth } from "@/hooks/useAuth";
import { HeaderCategories } from "./header-categories";
import Search from "./search";
import { useUserInfo } from "@/api/myuser/myuser.hooks";

export default function Header() {
  const { isLogin } = useAuth();
  const { data: user } = useUserInfo({ enabled: isLogin });
  return (
    <>
      <header className="sticky top-0 z-50 bg-white">
        <section className="bg-primary hidden p-1 text-center text-white md:block">
          با عضویت در کاستومی، اولین سفارش خود را ” رایگان” تحویل بگیرید
        </section>
        <section className="z-10 bg-white">
          <div className="p-2 md:p-5">
            <Container className="flex items-center justify-between gap-2">
              {/* Mobile Menu */}
              <MobileMenu />
              {/* Desktop Menu */}
              <div className="hidden w-36 shrink-0 md:block">
                <Link to={"/"}>
                  <DesktopLogoIcon className="h-9 w-full" />
                </Link>
              </div>
              <Search />
              <div>
                <div className="md:hidden">
                  <MobileLogoIcon className="size-14" />
                </div>
                <div className="hidden items-center justify-between md:flex md:flex-row">
                  <a href={isLogin ? "/profile" : "/auth/login"}>
                    <Button variant={"link"}>
                      <User />
                      {isLogin
                        ? `${user?.first_name} ${user?.last_name}`
                        : "حساب کاربری"}
                    </Button>
                  </a>
                  <Link to={"/checkout/cart"}>
                    <Button variant={"link"}>
                      <ShoppingCart />
                      سبد خرید
                    </Button>
                  </Link>
                </div>
              </div>
            </Container>
          </div>
        </section>
        <HeaderCategories />
      </header>
      <div className="md:h-12" />
    </>
  );
}
