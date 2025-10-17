import {
  ClipboardListIcon,
  HomeIcon,
  ShoppingBagIcon,
  TagIcon,
} from "lucide-react";
import { NavLink } from "react-router";

// If you don't have heroicons: npm install @heroicons/react

const navigationLinks = [
  { name: "داشبورد", href: "/store-admin", icon: HomeIcon },
  { name: "دسته بندی ها", href: "/store-admin/categories", icon: TagIcon },
  { name: "محصولات", href: "/store-admin/products", icon: ShoppingBagIcon },
  {
    name: "محصولات فروشگاه من",
    href: "/store-admin/store-products",
    icon: ShoppingBagIcon,
  },
  { name: "سفارشات", href: "/store-admin/orders", icon: ClipboardListIcon },
];

export default function Sidebar() {
  const baseLinkClasses =
    "flex items-center px-3 py-3 text-gray-300 hover:bg-gray-700 hover:text-white rounded-md transition-colors duration-150";
  const activeLinkClasses = "bg-gray-900 text-white";
  const inactiveLinkClasses = "text-gray-400"; // Or your preferred inactive state

  return (
    <div className="fixed top-0 right-0 flex h-screen w-64 flex-col overflow-y-auto bg-gray-800 text-white">
      <div className="border-b border-gray-700 p-5">
        <h1 className="text-2xl font-semibold text-white">ادمین فروشگاه</h1>
      </div>
      <nav className="flex-grow space-y-2 p-4">
        {navigationLinks.map((item) => (
          <NavLink
            key={item.name}
            to={item.href}
            end={item.href === "/store-admin"} // Ensures only exact match for dashboard
            className={({ isActive }) =>
              `${baseLinkClasses} ${isActive ? activeLinkClasses : inactiveLinkClasses}`
            }
          >
            {item.icon && (
              <item.icon className="ml-3 h-6 w-6" aria-hidden="true" />
            )}
            {item.name}
          </NavLink>
        ))}
      </nav>
      <div className="mt-auto border-t border-gray-700 p-4">
        {/* You can add footer items here, like a logout button or user profile */}
        <p className="text-sm text-gray-500">
          © {new Date().getFullYear()} Your Shop
        </p>
      </div>
    </div>
  );
}
