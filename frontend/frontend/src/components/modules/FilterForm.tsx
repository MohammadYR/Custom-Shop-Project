import { ProductsQueryFilter } from "@/types";
import InputWithLabel from "../ui/input-with-label";
import { ChangeEvent } from "react";

type FilterFormProps = {
  query: Partial<ProductsQueryFilter> | undefined;
  setQuery: React.Dispatch<
    React.SetStateAction<Partial<ProductsQueryFilter> | undefined>
  >;
};
// TODO: add debounce
export default function FilterForm({ query, setQuery }: FilterFormProps) {
  const handleChange = (e: ChangeEvent<HTMLInputElement>) => {
    setQuery((old) => ({ ...old, [e.target.name]: e.target.value }));
  };
  return (
    <div className="">
      <div className="flex items-center justify-between">
        <div>فیلتر ها</div>
        <div>حذف فیلترها</div>
      </div>
      <form>
        <div className="my-2 flex flex-col gap-2">
          <div>
            <InputWithLabel
              name="name"
              label="نام"
              value={query?.name || ""}
              onChange={handleChange}
            />
          </div>
          <div>
            <InputWithLabel
              label="حداکثر قیمت"
              onChange={handleChange}
              name="price_max"
            />
          </div>
          <div>
            <InputWithLabel
              name="price_min"
              label="حداقل قیمت"
              onChange={handleChange}
            />
          </div>
        </div>
      </form>
    </div>
  );
}
