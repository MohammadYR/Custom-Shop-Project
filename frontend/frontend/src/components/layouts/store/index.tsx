import { Outlet, useNavigate } from "react-router";
import withSuspense from "@/components/withSuspend";
import { lazy, useEffect } from "react";
import { Toaster } from "@/components/ui/sonner";
import { useAuth } from "@/hooks/useAuth";
const Sidebar = withSuspense(lazy(() => import("./sidebar")));

export default function DashboardLayout() {
  const navigate = useNavigate();
  const { isLogin } = useAuth();
  useEffect(() => {
    if (!isLogin) {
      navigate("/");
    }
  }, [isLogin, navigate]);
  return (
    <div className="flex h-screen bg-gray-100">
      <Sidebar />
      <main className="mr-64 flex-1 overflow-x-hidden overflow-y-auto bg-gray-100">
        <div className="p-6">
          <Outlet />
        </div>
        <Toaster position="top-center" />
      </main>
    </div>
  );
}
