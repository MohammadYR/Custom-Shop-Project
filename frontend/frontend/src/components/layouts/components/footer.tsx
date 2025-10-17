import {
  FacebookIcon,
  HomeIcon,
  Instagram,
  ShoppingCartIcon,
  UserIcon,
  Youtube,
} from "lucide-react";

export default function Footer() {
  return (
    <footer className="bg-primary mb-16 text-white md:mb-0">
      {/* Top Section - Social & Newsletter */}
      <section className="hidden md:block">
        <section className="mt-1.5 bg-[#5b1619]">
          <div className="mx-auto flex max-w-7xl flex-col items-center justify-between gap-6 px-4 py-6 md:flex-row-reverse">
            {/* Social Links */}
            <div className="text-center md:text-right">
              <p className="mb-2">ما را در شبکه های اجتماعی دنبال کنید</p>
              <div className="flex justify-center gap-4 text-2xl md:justify-end">
                <a href="#">
                  <Instagram strokeWidth={1} />
                </a>
                <a href="#">
                  <FacebookIcon strokeWidth={1} />
                </a>
                <a href="#">
                  <Youtube strokeWidth={1} />
                </a>
              </div>
            </div>

            {/* Newsletter */}
            <div className="w-full text-center md:w-auto md:text-left">
              <p className="mb-2">
                برای دریافت آخرین اخبار و تخفیف های جدید،ایمیل خود را وارد
                نمایید
              </p>
              <div className="flex items-center justify-center gap-2 md:justify-start">
                <input
                  type="email"
                  placeholder="ایمیل شما"
                  className="w-full rounded border bg-transparent px-4 py-2 text-white placeholder:text-gray-300 focus:outline-none"
                />
                <button className="rounded bg-[#a73b40] px-4 py-2 hover:bg-[#902f33]">
                  ثبت
                </button>
              </div>
            </div>
          </div>
        </section>

        {/* Middle Section - Links */}
        <div className="py-8">
          <div className="mx-auto grid max-w-7xl grid-cols-1 gap-6 px-4 text-center sm:grid-cols-2 md:grid-cols-4 md:text-right">
            {/* Column 1 */}
            <div>
              <h3 className="mb-2 font-bold">همراه با کاستومی</h3>
              <ul className="space-y-1">
                <li>
                  <a href="#">فروش محصولات</a>
                </li>
                <li>
                  <a href="#">فرصت همکاری</a>
                </li>
                <li>
                  <a href="#">تماس با ما</a>
                </li>
                <li>
                  <a href="#">نقشه سایت</a>
                </li>
              </ul>
            </div>
            {/* Column 2 */}
            <div>
              <h3 className="mb-2 font-bold">خدمات مشتریان</h3>
              <ul className="space-y-1">
                <li>
                  <a href="#">سوالات متداول</a>
                </li>
                <li>
                  <a href="#">حریم خصوصی</a>
                </li>
                <li>
                  <a href="#">ثبت شکایت</a>
                </li>
                <li>
                  <a href="#">ضمانت نامه محصولات</a>
                </li>
              </ul>
            </div>
            {/* Column 3 */}
            <div>
              <h3 className="mb-2 font-bold">راهنمای خرید</h3>
              <ul className="space-y-1">
                <li>
                  <a href="#">راهنمای ثبت سفارش</a>
                </li>
                <li>
                  <a href="#">شیوه های پرداخت</a>
                </li>
                <li>
                  <a href="#">نحوه ارسال سفارش ها</a>
                </li>
                <li>
                  <a href="#">شرایط بازگرداندن محصول</a>
                </li>
              </ul>
            </div>
            {/* Column 4 */}
            <div className="flex flex-col items-center gap-2 md:items-end">
              <h3 className="mb-2 font-bold">فروشگاه اینترنتی کاستومی</h3>
              <p>پاسخگویی ۲۴ ساعته، ۷ روز هفته</p>
              <p>۰۲۱-۳۴۵۶۰۰۰۰</p>
              <div className="mt-2 flex gap-2">
                <img src="/badge1.png" alt="نماد" className="h-12" />
                <img src="/badge2.png" alt="نماد" className="h-12" />
                <img src="/badge3.png" alt="نماد" className="h-12" />
              </div>
            </div>
          </div>
        </div>

        {/* Bottom Section - Copyright */}
        <div className="py-4 text-center text-sm">
          <p>تمام حقوق این وب‌سایت متعلق به فروشگاه آنلاین کاستومی می باشد</p>
        </div>
      </section>
      <nav className="fixed bottom-0 left-0 flex w-full justify-around border-gray-300 bg-white p-2 md:hidden">
        <a href="/" className="flex flex-col items-center text-gray-700">
          <HomeIcon className="size-6" />
          <span className="text-xs">خانه</span>
        </a>
        <a href="/cart" className="flex flex-col items-center text-gray-700">
          <ShoppingCartIcon className="size-6" />
          <span className="text-xs">سبد خرید</span>
        </a>
        <a href="/profile" className="flex flex-col items-center text-gray-700">
          <UserIcon className="size-6" />
          <span className="text-xs">پروفایل</span>
        </a>
      </nav>
    </footer>
  );
}
