import { useState } from "react";

export interface CursorPaginationState {
  /**
   * The user's `display_name` used for pagination.
   */
  cursor: string;

  /**
   * The pagination direction.
   */
  direction: "forward" | "back";
}

export const useCursorPagination = () => {
  const [pagination, setPagination] = useState<CursorPaginationState>({ cursor: "", direction: "forward" });

  const toPreviousPage = (data: undefined | { prev?: string; next?: string }) => {
    setPagination({
      cursor: data?.prev || "",
      direction: "back",
    });
  };

  const toNextPage = (data: undefined | { prev?: string; next?: string }) => {
    setPagination({
      cursor: data?.next || "",
      direction: "forward",
    });
  };

  const resetCursor = () => setPagination((old) => ({ ...old, cursor: "" }));

  return {
    pagination,
    toNextPage,
    toPreviousPage,
    resetCursor,
  };
};
