import { Box, CircularProgress, Flex, IconButton, Link, Tooltip } from "@chakra-ui/react";
import { createColumnHelper } from "@tanstack/react-table";
import { Mail, ThumbsDown, ThumbsUp, User } from "lucide-react";
import NextLink from "next/link";
import { FetchTrollBoardResponse, TrollboardEntity, TrollboardTimeFrame } from "src/types/Trollboard";

import { DataTable, DataTableColumnDef } from "../DataTable/DataTable";
import { createJsonExpandRowModel } from "../DataTable/jsonExpandRowModel";
import { Discord } from "../Icons/Discord";
import { useBoardPagination } from "./useBoardPagination";
import { useBoardRowProps } from "./useBoardRowProps";
import { useFetchBoard } from "./useFetchBoard";

const columnHelper = createColumnHelper<TrollboardEntity>();
const toPercentage = (num: number) => `${Math.round(num * 100)}%`;
const jsonExpandRowModel = createJsonExpandRowModel<TrollboardEntity>();

const columns: DataTableColumnDef<TrollboardEntity>[] = [
  {
    ...columnHelper.accessor("rank", {
      cell: jsonExpandRowModel.renderCell,
    }),
    span: jsonExpandRowModel.span,
  },
  columnHelper.accessor("display_name", {
    header: "Display name",
    cell: ({ getValue, row }) => {
      const isEmail = row.original.auth_method === "local";
      return (
        <Flex gap="2" alignItems="center">
          <Link as={NextLink} href={`/admin/manage_user/${row.original.user_id}`}>
            {getValue()}
          </Link>
          <Tooltip label={`This user signin with ${isEmail ? "email" : "discord"}`}>
            {isEmail ? <Mail size="20"></Mail> : <Discord size="20"></Discord>}
          </Tooltip>
        </Flex>
      );
    },
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
  columnHelper.accessor("toxicity", {
    cell: ({ getValue }) => toPercentage(getValue() || 0),
  }),
  columnHelper.accessor((row) => row.user_id, {
    header: "Actions",
    cell: ({ row }) => (
      <IconButton
        as={NextLink}
        href={`/admin/manage_user/${row.original.user_id}`}
        aria-label={"View user"}
        icon={<User></User>}
      ></IconButton>
    ),
  }),
];

export const TrollboardTable = ({
  limit,
  rowPerPage,
  timeFrame,
  enabled,
}: {
  timeFrame: TrollboardTimeFrame;
  limit: number;
  rowPerPage: number;
  enabled: boolean;
}) => {
  const {
    data: trollboardRes,
    isLoading,
    error,
    lastUpdated,
  } = useFetchBoard<FetchTrollBoardResponse>(
    `/api/admin/trollboard?time_frame=${timeFrame}&limit=${limit}&enabled=${enabled}`
  );

  const { data, ...paginationProps } = useBoardPagination<TrollboardEntity>({
    rowPerPage,
    data: jsonExpandRowModel.toExpandable(trollboardRes?.trollboard),
    limit,
  });
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
      <DataTable
        data={data}
        columns={columns}
        caption={lastUpdated}
        rowProps={rowProps}
        getSubRows={jsonExpandRowModel.getSubRows}
        {...paginationProps}
      ></DataTable>
    </Box>
  );
};
