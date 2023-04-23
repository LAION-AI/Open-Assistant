import { useRef, useEffect, useMemo } from "react";
import { get } from "src/lib/api";
import { GetChatsResponse } from "src/types/Chat";
import useSWRInfinite from "swr/infinite";

export function useListChatPagination(initialChats?: GetChatsResponse) {
  const {
    data: responses,
    mutate: mutateChatResponses,
    setSize,
    isLoading,
  } = useSWRInfinite<GetChatsResponse>(
    (pageIndex, previousPageData: GetChatsResponse) => {
      if (!previousPageData && pageIndex === 0) return `/api/chat?limit=20`; // initial call
      if (previousPageData && !previousPageData.next) return null; // reached the end
      return `/api/chat?limit=20&after=${previousPageData.next}`; // paginated call
    },
    get,
    {
      keepPreviousData: true,
      revalidateFirstPage: false,
      fallbackData: initialChats ? [initialChats] : undefined,
    }
  );
  const loadMoreRef = useRef(null);
  const isEnd = useMemo(() => !responses?.[responses.length - 1]?.next, [responses]);

  useEffect(() => {
    const handleObserver = (entities) => {
      const target = entities[0];
      if (target.isIntersecting && !isLoading && !isEnd) {
        setSize((size) => {
          return size + 1;
        });
      }
    };
    const observer = new IntersectionObserver(handleObserver);

    if (loadMoreRef.current) observer.observe(loadMoreRef.current);

    return () => {
      if (loadMoreRef.current) observer.unobserve(loadMoreRef.current);
    };
  }, [isLoading, isEnd]);

  return { loadMoreRef, responses, mutateChatResponses };
}
