import { Box, CircularProgress, Flex, Link, useColorModeValue } from "@chakra-ui/react";
import { createColumnHelper } from "@tanstack/react-table";
import { MoreHorizontal } from "lucide-react";
import NextLink from "next/link";
import { useTranslation } from "next-i18next";
import React, { useMemo } from "react";
import Image from "next/image";
import { useHasAnyRole } from "src/hooks/auth/useHasAnyRole";
import { LeaderboardEntity, LeaderboardReply, LeaderboardTimeFrame } from "src/types/Leaderboard";

import { DataTable, DataTableColumnDef } from "../DataTable/DataTable";
import { createJsonExpandRowModel } from "../DataTable/jsonExpandRowModel";
import { useBoardPagination } from "./useBoardPagination";
import { useBoardRowProps } from "./useBoardRowProps";
import { useFetchBoard } from "./useFetchBoard";
import { UserAvatar } from "../UserAvatar";
type WindowLeaderboardEntity = LeaderboardEntity & { isSpaceRow?: boolean };

const columnHelper = createColumnHelper<WindowLeaderboardEntity>();
const jsonExpandRowModel = createJsonExpandRowModel<WindowLeaderboardEntity>();
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

  const isAdminOrMod = useHasAnyRole(["admin", "moderator"]);

  const columns: DataTableColumnDef<WindowLeaderboardEntity>[] = useMemo(
    () => [
      {
        ...columnHelper.accessor("rank", {
          header: t("rank"),
          cell: (ctx) =>
            ctx.row.original.isSpaceRow ? (
              <SpaceRow></SpaceRow>
            ) : isAdminOrMod ? (
              jsonExpandRowModel.renderCell(ctx)
            ) : (
              ctx.getValue()
            ),
        }),
        span: (cell) => (cell.row.original.isSpaceRow ? 6 : jsonExpandRowModel.span(cell)),
      },
      columnHelper.accessor("display_name", {
        header: t("user"),
        cell: ({ getValue, row }) => (
          <div className="flex flex-row items-center gap-2">
            <UserAvatar displayName={getValue()} avatarUrl={row.original.image}></UserAvatar>
            {isAdminOrMod ? (
              <Link as={NextLink} href={`/admin/manage_user/${row.original.user_id}`}>
                {getValue()}
              </Link>
            ) : (
              getValue()
            )}
          </div>
        ),
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
    [isAdminOrMod, t]
  );

  const {
    data: paginatedData,
    end,
    ...pagnationProps
  } = useBoardPagination({ rowPerPage, data: jsonExpandRowModel.toExpandable(reply?.leaderboard || []), limit });
  const data = useMemo(() => {
    if (hideCurrentUserRanking || !reply?.user_stats_window || reply.user_stats_window.length === 0) {
      return paginatedData;
    }
    const userStatsWindow: WindowLeaderboardEntity[] = jsonExpandRowModel.toExpandable(reply.user_stats_window);
    const userStats = userStatsWindow.find((stats) => stats.highlighted);
    if (userStats && userStats.rank > end) {
      paginatedData.push(
        { isSpaceRow: true } as WindowLeaderboardEntity,
        ...userStatsWindow.filter(
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
      getSubRows={jsonExpandRowModel.getSubRows}
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
