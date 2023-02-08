import { Box, CircularProgress, Flex, IconButton, Link, Tooltip } from "@chakra-ui/react";
import { createColumnHelper } from "@tanstack/react-table";
import { Mail, ThumbsDown, ThumbsUp, User } from "lucide-react";
import NextLink from "next/link";
import { FetchTrollBoardResponse, TrollboardEntity, TrollboardTimeFrame } from "src/types/Trollboard";
import { ElementOf } from "src/types/utils";

import { DataTable, DataTableColumnDef } from "../DataTable/DataTable";
import { createJsonExpandRowModel } from "../DataTable/jsonExpandRowModel";
import { Discord } from "../Icons/Discord";
import { useBoardPagination } from "./useBoardPagination";
import { useBoardRowProps } from "./useBoardRowProps";
import { useFetchBoard } from "./useFetchBoard";

type ExpandableTrollboardEntity = TrollboardEntity;

const columnHelper = createColumnHelper<ExpandableTrollboardEntity>();
const toPercentage = (num: number) => `${Math.round(num * 100)}%`;
const jsonExpandRowModel = createJsonExpandRowModel<ExpandableTrollboardEntity>();

const columns: DataTableColumnDef<ExpandableTrollboardEntity>[] = [
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
  // columnHelper.accessor("lang_mismach", {
  //   header: "Lang mismach",
  // }),
  // columnHelper.accessor("not_appropriate", {
  //   header: "Not appropriate",
  // }),
  // columnHelper.accessor("pii", {}),
  // columnHelper.accessor("hate_speech", {
  //   header: "Hate speech",
  // }),
  // columnHelper.accessor("sexual_content", {
  //   header: "Sexual",
  // }),
  // columnHelper.accessor("political_content", {
  //   header: "Political",
  // }),
  columnHelper.accessor("toxicity", {
    cell: ({ getValue }) => toPercentage(getValue() || 0),
  }),
  // columnHelper.accessor("quality", {
  //   cell: ({ getValue }) => toPercentage(getValue() || 0),
  // }),
  // columnHelper.accessor("helpfulness", {
  //   cell: ({ getValue }) => toPercentage(getValue() || 0),
  // }),
  // columnHelper.accessor("humor", {
  //   cell: ({ getValue }) => toPercentage(getValue() || 0),
  // }),
  // columnHelper.accessor("violence", {
  //   cell: ({ getValue }) => toPercentage(getValue() || 0),
  // }),
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

  const { data, ...paginationProps } = useBoardPagination<ExpandableTrollboardEntity>({
    rowPerPage,
    data: jsonExpandRowModel.toExpandable(trollboardRes?.trollboard),
    limit,
  });
  const rowProps = useBoardRowProps<ExpandableTrollboardEntity>();
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
      <DataTable<ElementOf<typeof data>>
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
