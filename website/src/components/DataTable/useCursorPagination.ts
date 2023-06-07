import { useCallback, useState } from "react";

export type CursorPaginationState = {
  /**
   * The user's `display_name` used for pagination.
   */
  cursor: string;

  /**
   * The pagination direction.
   */
  direction: "forward" | "back";
};

export const useCursorPagination = () => {
  const [pagination, setPagination] = useState<CursorPaginationState>({ cursor: "", direction: "forward" });

  const toPreviousPage = useCallback(
    (data: undefined | { prev?: string; next?: string }) => {
      setPagination({
        cursor: data?.prev || "",
        direction: "back",
      });
    },
    [setPagination]
  );

  const toNextPage = useCallback(
    (data: undefined | { prev?: string; next?: string }) => {
      setPagination({
        cursor: data?.next || "",
        direction: "forward",
      });
    },
    [setPagination]
  );

  const resetCursor = useCallback(() => setPagination((old) => ({ ...old, cursor: "" })), []);

  return {
    pagination,
    toNextPage,
    toPreviousPage,
    resetCursor,
  };
};
