import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group";
import { ProductDetails } from "@/types";

export function ProductImage({ product }: { product: ProductDetails }) {
  return (
    <div
      className="shrink-0 overflow-hidden md:flex md:flex-row-reverse"
      dir="rtl"
    >
      {/* Main Product Image */}
      <div className="w-full p-5">
        <div className="bg-muted relative w-full overflow-hidden rounded-md shadow-lg md:size-[400px]">
          <img
            src={product.images[0]?.image}
            className="h-full w-full object-cover"
            alt="Product"
          />
          <div className="absolute right-0 bottom-0 left-0 z-10 bg-white/50 backdrop-blur-md">
            <RadioGroup
              className="flex justify-center p-3"
              defaultValue="amber-one"
            >
              <RadioGroupItem className="bg-amber-400 p-3" value="amber-one" />
              <RadioGroupItem className="bg-red-500 p-3" value="red-two" />
              <RadioGroupItem className="bg-green-500 p-3" value="green-two" />
              <RadioGroupItem className="bg-black p-3" value="black" />
              <RadioGroupItem className="bg-white p-3" value="white" />
            </RadioGroup>
          </div>
        </div>
      </div>

      {/* Thumbnail List */}
      <div className="flex h-fit flex-nowrap gap-2 overflow-auto p-5 md:my-5 md:w-[150px] md:flex-col md:p-0">
        {product.images.map((item) => (
          <div key={item.id}>
            <img
              className="h-22 rounded object-contain"
              src={item.image}
              alt={`Thumbnail`}
            />
          </div>
        ))}
      </div>
    </div>
  );
}
