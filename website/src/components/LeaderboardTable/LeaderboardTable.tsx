import { Box, CircularProgress, Flex, useColorModeValue } from "@chakra-ui/react";
import { createColumnHelper } from "@tanstack/react-table";
import { MoreHorizontal } from "lucide-react";
import { useTranslation } from "next-i18next";
import React, { useMemo } from "react";
import { LeaderboardEntity, LeaderboardReply, LeaderboardTimeFrame } from "src/types/Leaderboard";

import { DataTable, DataTableColumnDef } from "../DataTable";
import { useBoardPagination } from "./useBoardPagination";
import { useBoardRowProps } from "./useBoardRowProps";
import { useFetchBoard } from "./useFetchBoard";

type WindowLeaderboardEntity = LeaderboardEntity & { isSpaceRow?: boolean };

const columnHelper = createColumnHelper<WindowLeaderboardEntity>();

/**
 * Presents a grid of leaderboard entries with more detailed information.
 */
export const LeaderboardTable = ({
  timeFrame,
  limit: limit,
  rowPerPage,
  hideCurrentUserRanking,
}: {
  timeFrame: LeaderboardTimeFrame;
  limit: number;
  rowPerPage: number;
  hideCurrentUserRanking?: boolean;
}) => {
  const { t } = useTranslation("leaderboard");

  const {
    data: reply,
    isLoading,
    error,
    lastUpdated,
  } = useFetchBoard<LeaderboardReply & { user_stats_window?: LeaderboardReply["leaderboard"] }>(
    `/api/leaderboard?time_frame=${timeFrame}&limit=${limit}&includeUserStats=${!hideCurrentUserRanking}`
  );
  const columns: DataTableColumnDef<WindowLeaderboardEntity>[] = useMemo(
    () => [
      {
        ...columnHelper.accessor("rank", {
          header: t("rank"),
          cell: ({ row, getValue }) => (row.original.isSpaceRow ? <SpaceRow></SpaceRow> : getValue()),
        }),
        span: (cell) => (cell.row.original.isSpaceRow ? 6 : undefined),
      },
      columnHelper.accessor("display_name", {
        header: t("user"),
      }),
      columnHelper.accessor("leader_score", {
        header: t("score"),
      }),
      columnHelper.accessor("prompts", {
        header: t("prompt"),
      }),
      columnHelper.accessor((row) => row.replies_assistant + row.replies_prompter, {
        header: t("reply"),
      }),
      columnHelper.accessor((row) => row.labels_full + row.labels_simple, {
        header: t("label"),
      }),
    ],
    [t]
  );

  const {
    data: paginatedData,
    end,
    ...pagnationProps
  } = useBoardPagination({ rowPerPage, data: reply?.leaderboard, limit });
  const data: WindowLeaderboardEntity[] = useMemo(() => {
    if (hideCurrentUserRanking || !reply?.user_stats_window) {
      return paginatedData;
    }
    const userStatsWindow: WindowLeaderboardEntity[] = reply.user_stats_window;
    const userStats = userStatsWindow.find((stats) => stats.highlighted);
    if (userStats && userStats.rank > end) {
      paginatedData.push(
        { isSpaceRow: true } as WindowLeaderboardEntity,
        ...reply.user_stats_window.filter(
          (stats) => paginatedData.findIndex((leaderBoardEntity) => leaderBoardEntity.user_id === stats.user_id) === -1
        ) // filter to avoid duplicated row
      );
    }
    return paginatedData;
  }, [hideCurrentUserRanking, reply?.user_stats_window, end, paginatedData]);

  const rowProps = useBoardRowProps<WindowLeaderboardEntity>();

  if (isLoading) {
    return <CircularProgress isIndeterminate></CircularProgress>;
  }

  if (error) {
    return <span>Unable to load leaderboard</span>;
  }

  return (
    <DataTable<WindowLeaderboardEntity>
      data={data}
      columns={columns}
      caption={lastUpdated}
      rowProps={rowProps}
      {...pagnationProps}
    ></DataTable>
  );
};

const SpaceRow = () => {
  const color = useColorModeValue("gray.600", "gray.400");
  return (
    <Flex justify="center">
      <Box as={MoreHorizontal} color={color}></Box>
    </Flex>
  );
};
