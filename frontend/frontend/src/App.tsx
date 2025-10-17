import "./App.css";
import { QueryClientProvider } from "@tanstack/react-query";
import { queryClient } from "./api/baseQuery";
import withSuspense from "./components/withSuspend";
import { lazy } from "react";
const AppRoutes = withSuspense(lazy(() => import("./routes")));
export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <AppRoutes />
    </QueryClientProvider>
  );
}
