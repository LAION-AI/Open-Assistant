import { Box, CircularProgress, Flex } from "@chakra-ui/react";
import { createColumnHelper } from "@tanstack/react-table";
import { ThumbsDown, ThumbsUp } from "lucide-react";
import { FetchTrollBoardResponse, TrollboardEntity, TrollboardTimeFrame } from "src/types/Trollboard";

import { DataTable } from "../DataTable";
import { useBoardPagination } from "./useBoardPagination";
import { useBoardRowProps } from "./useBoardRowProps";
import { useFetchBoard } from "./useFetchBoard";

const columnHelper = createColumnHelper<TrollboardEntity>();

const toPercentage = (num: number) => `${Math.round(num * 100)}%`;

const columns = [
  columnHelper.accessor("rank", {}),
  columnHelper.accessor("display_name", {
    header: "Display name",
  }),
  columnHelper.accessor("troll_score", {
    header: "Troll score",
  }),
  columnHelper.accessor("red_flags", {
    header: "Red flags",
  }),
  columnHelper.accessor((row) => [row.upvotes, row.downvotes] as const, {
    id: "vote",
    cell: ({ getValue }) => {
      const [up, down] = getValue();
      return (
        <Flex gap={2} justifyItems="center" alignItems="center">
          <ThumbsUp></ThumbsUp>
          {up}
          <ThumbsDown></ThumbsDown>
          {down}
        </Flex>
      );
    },
  }),
  columnHelper.accessor((row) => row.spam + row.spam_prompts, {
    header: "Spam",
  }),
  columnHelper.accessor("lang_mismach", {
    header: "Lang mismach",
  }),
  columnHelper.accessor("not_appropriate", {
    header: "Not appropriate",
  }),
  columnHelper.accessor("pii", {}),
  columnHelper.accessor("hate_speech", {
    header: "Hate speech",
  }),
  columnHelper.accessor("sexual_content", {
    header: "Sexual Content",
  }),
  columnHelper.accessor("political_content", {
    header: "Political Content",
  }),
  columnHelper.accessor("quality", {
    cell: ({ getValue }) => toPercentage(getValue()),
  }),
  columnHelper.accessor("helpfulness", {
    cell: ({ getValue }) => toPercentage(getValue()),
  }),
  columnHelper.accessor("humor", {
    cell: ({ getValue }) => toPercentage(getValue()),
  }),
  columnHelper.accessor("violence", {
    cell: ({ getValue }) => toPercentage(getValue()),
  }),
  columnHelper.accessor("toxicity", {
    cell: ({ getValue }) => toPercentage(getValue()),
  }),
];

export const TrollboardTable = ({
  limit,
  rowPerPage,
  timeFrame,
}: {
  timeFrame: TrollboardTimeFrame;
  limit: number;
  rowPerPage: number;
}) => {
  const {
    data: trollboardRes,
    isLoading,
    error,
    lastUpdated,
  } = useFetchBoard<FetchTrollBoardResponse>(`/api/admin/trollboard?time_frame=${timeFrame}&limit=${limit}`);

  const { data, ...paginationProps } = useBoardPagination({ rowPerPage, data: trollboardRes?.trollboard, limit });
  const rowProps = useBoardRowProps<TrollboardEntity>();
  if (isLoading) {
    return <CircularProgress isIndeterminate></CircularProgress>;
  }

  if (error) {
    return <span>Unable to load leaderboard</span>;
  }

  return (
    <Box
      sx={{
        "th,td": {
          px: 2,
        },
      }}
    >
      <DataTable<TrollboardEntity>
        data={data}
        columns={columns}
        caption={lastUpdated}
        rowProps={rowProps}
        {...paginationProps}
      ></DataTable>
    </Box>
  );
};
