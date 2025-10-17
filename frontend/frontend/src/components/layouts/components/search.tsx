import { useProducts } from "@/api/products/products.hooks";
import { Input } from "@/components/ui/input";
import { cn, showPersianNumber } from "@/lib/utils";
import { useState, useEffect, useRef } from "react"; // Added useEffect and useRef
import { Link } from "react-router";
import { useDebounceValue } from "usehooks-ts";

export default function Search() {
  const [show, setShow] = useState(false);
  const [name, setName] = useDebounceValue("", 500);

  const { data: products } = useProducts(
    { name },
    {
      enabled: !!name && show, // Only fetch when name is present and input is focused
    },
  );
  const searchContainerRef = useRef<HTMLDivElement>(null); // Ref for the main search container

  // Handle clicks outside the search component to close results
  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (
        searchContainerRef.current &&
        event.target &&
        !searchContainerRef.current.contains(event.target as Node)
      ) {
        setShow(false);
      }
    }
    // Bind the event listener
    document.addEventListener("mousedown", handleClickOutside);
    return () => {
      // Unbind the event listener on clean up
      document.removeEventListener("mousedown", handleClickOutside);
    };
  }, [searchContainerRef]);
  useEffect(() => {
    if (show) {
      document.body.classList.add("overflow-hidden");
    } else {
      document.body.classList.remove("overflow-hidden");
    }
  }, [show]);
  return (
    <div className="relative flex-grow" ref={searchContainerRef}>
      {/* Backdrop */}
      {show && (
        <div
          className={cn(
            "fixed inset-0 z-40 bg-black/30 transition-opacity duration-300 ease-in-out",
            show ? "opacity-100" : "pointer-events-none opacity-0",
          )}
          aria-hidden="true"
          onClick={() => setShow(false)} // Optionally close on backdrop click
        />
      )}

      <Input
        type="search"
        placeholder="جستجو"
        defaultValue={name}
        onChange={(e) => {
          setName(e.target.value);
          if (e.target.value) {
            setShow(true); // Show results as user types
          } else {
            // Optionally hide results if input is empty,
            // or let onBlur handle it. For now, keep it simple.
          }
        }}
        className="relative z-50 rounded-3xl" // Ensure input is above backdrop
        onFocus={() => {
          setShow(true);
        }}

        // onBlur is removed to rely on handleClickOutside
      />
      <div
        className={cn(
          "absolute z-50 mt-2 w-full overflow-hidden rounded-md bg-white p-6 shadow-2xl transition-all duration-300 ease-in-out", // Ensure results are above backdrop
          show
            ? "max-h-96 opacity-100"
            : "pointer-events-none max-h-0 opacity-0", // Added opacity and pointer-events
        )}
      >
        {show && !name && <div> نام کالا رو وارد کن تا برات پیداش کنم</div>}

        {show &&
          name &&
          products?.results &&
          products.results.length > 0 &&
          products.results.map((item) => (
            <div
              key={item.id}
              className="my-2 cursor-pointer overflow-auto p-2 hover:bg-gray-100"
            >
              <Link
                to={`/products/${item.id}`}
                onClick={() => {
                  setShow(false);
                  setName("");
                }}
              >
                <div className="flex gap-2">
                  <img
                    width={64}
                    height={64}
                    src={item.images[0]?.image}
                    alt={item.name}
                  />
                  <div>
                    <div>{item.name}</div>
                    <div className="mt-3">
                      {showPersianNumber(item.best_price || 0)} تومان
                    </div>
                  </div>
                </div>
              </Link>
            </div>
          ))}
        {show && name && products?.results && products.results.length === 0 && (
          <div className="p-2 text-gray-500">No results found.</div>
        )}
        {show &&
          !products && ( // Loading state or initial state before data
            <div className="p-2 text-gray-500">Loading...</div>
          )}
      </div>
    </div>
  );
}
