import {
  Pagination,
  PaginationContent,
  PaginationEllipsis,
  PaginationItem,
  PaginationLink,
  PaginationNext,
  PaginationPrevious,
} from "@/components/ui/pagination";
import { cn } from "@/lib/utils";
import { useMemo } from "react";
type PaginationControlProps = {
  total?: number;
  pageSize?: number;
  currentPage: number;
  setCurrentPage: (newPage: number) => void;
};
export function PaginationControl({
  total = 0,
  pageSize = 10,
  currentPage = 1,
  setCurrentPage,
}: PaginationControlProps) {
  const totalPages = useMemo(() => {
    if (pageSize === 0) {
      return 0;
    }
    if (!total) {
      return 0;
    }
    return Math.ceil(total / pageSize);
  }, [total, pageSize]);

  if (total < pageSize) {
    return null;
  }
  return (
    <Pagination>
      <PaginationContent>
        <PaginationItem>
          <PaginationPrevious
            onClick={() => setCurrentPage(currentPage - 1)}
            href="#"
          >
            صفحه قبل
          </PaginationPrevious>
        </PaginationItem>
        {currentPage > 2 && (
          <PaginationItem>
            <PaginationEllipsis />
          </PaginationItem>
        )}
        {currentPage > 1 && (
          <PaginationItem>
            <PaginationLink
              href="#"
              onClick={() => setCurrentPage(currentPage - 1)}
            >
              {currentPage - 1}
            </PaginationLink>
          </PaginationItem>
        )}
        <PaginationItem>
          <PaginationLink href="#" isActive>
            {currentPage}
          </PaginationLink>
        </PaginationItem>
        <PaginationItem
          className={cn(currentPage + 1 > totalPages && "hidden")}
        >
          <PaginationLink
            href="#"
            onClick={() => setCurrentPage(currentPage + 1)}
          >
            {currentPage + 1}
          </PaginationLink>
        </PaginationItem>
        <PaginationItem
          className={cn(currentPage > totalPages - 2 && "hidden")}
        >
          <PaginationEllipsis />
        </PaginationItem>
        <PaginationItem className={cn(currentPage >= totalPages && "hidden")}>
          <PaginationNext
            onClick={() => setCurrentPage(currentPage + 1)}
            href="#"
          >
            صفحه بعد
          </PaginationNext>
        </PaginationItem>
      </PaginationContent>
    </Pagination>
  );
}
