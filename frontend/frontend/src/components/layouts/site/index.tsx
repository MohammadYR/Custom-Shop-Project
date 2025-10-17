import { lazy } from "react";
import withSuspense from "@/components/withSuspend";
const Header = withSuspense(lazy(() => import("../components/header")));
const Footer = withSuspense(lazy(() => import("../components/footer")));

import { Outlet } from "react-router";
import { Toaster } from "@/components/ui/sonner";
export default function StoreLayout() {
  return (
    <>
      <Header />
      <Outlet />
      <Toaster position="top-center" />
      <Footer />
    </>
  );
}
