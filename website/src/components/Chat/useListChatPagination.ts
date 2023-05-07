import { useEffect, useMemo, useRef } from "react";
import { get } from "src/lib/api";
import { API_ROUTES } from "src/lib/routes";
import { GetChatsResponse } from "src/types/Chat";
import useSWRInfinite from "swr/infinite";

export type ChatListViewSelection = "visible" | "visible_hidden";

export function useListChatPagination(view: ChatListViewSelection) {
  const {
    data: responses,
    mutate: mutateChatResponses,
    setSize,
    isLoading,
  } = useSWRInfinite<GetChatsResponse>(
    (pageIndex, previousPageData: GetChatsResponse) => {
      const params = { include_hidden: view === "visible_hidden" };
      if (!previousPageData && pageIndex === 0) return API_ROUTES.LIST_CHAT_WITH_PARMS(params); // initial call
      if (previousPageData && !previousPageData.next) return null; // reached the end
      return API_ROUTES.LIST_CHAT_WITH_PARMS({ ...params, after: previousPageData.next }); // paginated call
    },
    get,
    {
      keepPreviousData: true,
      revalidateFirstPage: false,
    }
  );
  const loadMoreRef = useRef(null);
  const isEnd = useMemo(() => !responses?.[responses.length - 1]?.next, [responses]);

  useEffect(() => {
    const handleObserver: IntersectionObserverCallback = (entries) => {
      const target = entries[0];
      if (target.isIntersecting && !isLoading && !isEnd) {
        setSize((size) => size + 1);
      }
    };
    const observer = new IntersectionObserver(handleObserver);

    if (loadMoreRef.current) observer.observe(loadMoreRef.current);

    return () => observer.disconnect();
  }, [isLoading, isEnd, setSize]);

  return { loadMoreRef, responses, mutateChatResponses };
}
