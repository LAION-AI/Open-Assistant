import { useState } from "react";

export const useBoardPagination = <T>({
  rowPerPage,
  limit,
  ...res
}: {
  rowPerPage: number;
  data?: T[];
  limit: number;
}) => {
  const data = res.data || [];
  const [page, setPage] = useState(1);
  const maxPage = data ? Math.ceil(data.length / rowPerPage) : 0;
  const disablePagination = limit <= rowPerPage;
  const disableNext = page >= maxPage;
  const disablePrevious = page === 1;
  const onNextClick = () => setPage((p) => p + 1);
  const onPreviousClick = () => setPage((p) => p - 1);
  const start = (page - 1) * rowPerPage;
  const end = start + rowPerPage;
  const entities = data.slice(start, end);

  return {
    page,
    data: entities,
    end,
    disablePrevious,
    disableNext,
    disablePagination,
    onNextClick,
    onPreviousClick,
  };
};
