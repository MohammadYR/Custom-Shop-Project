import { SITE_TITLE } from "@/configs";
import { useEffect } from "react";

export function useSiteTitle(title?: string) {
  useEffect(() => {
    if (title) {
      document.title = SITE_TITLE + " " + title;
    }
  }, [title]);
}
