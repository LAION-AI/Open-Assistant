import { Box, CircularProgress, Flex, useColorModeValue, useToken } from "@chakra-ui/react";
import { createColumnHelper } from "@tanstack/react-table";
import { MoreHorizontal } from "lucide-react";
import { useTranslation } from "next-i18next";
import React, { useCallback, useMemo, useState } from "react";
import { get } from "src/lib/api";
import { colors } from "src/styles/Theme/colors";
import { LeaderboardEntity, LeaderboardReply, LeaderboardTimeFrame } from "src/types/Leaderboard";
import useSWRImmutable from "swr/immutable";

import { DataTable, DataTableColumnDef, DataTableRowPropsCallback } from "../DataTable";

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
  } = useSWRImmutable<LeaderboardReply & { user_stats_window?: LeaderboardReply["leaderboard"] }>(
    `/api/leaderboard?time_frame=${timeFrame}&limit=${limit}&includeUserStats=${!hideCurrentUserRanking}`,
    get
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

  const lastUpdated = useMemo(() => {
    const val = new Date(reply?.last_updated);
    return t("last_updated_at", { val, formatParams: { val: { dateStyle: "full", timeStyle: "short" } } });
  }, [t, reply?.last_updated]);

  const [page, setPage] = useState(1);
  const data: WindowLeaderboardEntity[] = useMemo(() => {
    if (!reply) {
      return [];
    }
    const start = (page - 1) * rowPerPage;
    const end = start + rowPerPage;
    const leaderBoardEntities = reply.leaderboard.slice(start, end);
    if (hideCurrentUserRanking || !reply.user_stats_window) {
      return leaderBoardEntities;
    }
    const userStatsWindow: WindowLeaderboardEntity[] = reply.user_stats_window;
    const userStats = userStatsWindow.find((stats) => stats.highlighted);
    if (userStats.rank > end) {
      leaderBoardEntities.push(
        { isSpaceRow: true } as WindowLeaderboardEntity,
        ...reply.user_stats_window.filter(
          (stats) =>
            leaderBoardEntities.findIndex((leaderBoardEntity) => leaderBoardEntity.user_id === stats.user_id) === -1
        ) // filter to avoid duplicated row
      );
    }
    return leaderBoardEntities;
  }, [page, rowPerPage, reply, hideCurrentUserRanking]);

  const rowProps = useLeaderboardRowProps();

  if (isLoading) {
    return <CircularProgress isIndeterminate></CircularProgress>;
  }

  if (error) {
    return <span>Unable to load leaderboard</span>;
  }

  const maxPage = Math.ceil(reply.leaderboard.length / rowPerPage);

  return (
    <DataTable
      data={data}
      columns={columns}
      caption={lastUpdated}
      disablePagination={limit <= rowPerPage}
      disableNext={page >= maxPage}
      disablePrevious={page === 1}
      onNextClick={() => setPage((p) => p + 1)}
      onPreviousClick={() => setPage((p) => p - 1)}
      rowProps={rowProps}
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

const useLeaderboardRowProps = () => {
  const borderColor = useToken("colors", useColorModeValue(colors.light.active, colors.dark.active));
  return useCallback<DataTableRowPropsCallback<WindowLeaderboardEntity>>(
    (row) => {
      const rowData = row.original;
      return rowData.highlighted
        ? {
            sx: {
              // https://stackoverflow.com/questions/37963524/how-to-apply-border-radius-to-tr-in-bootstrap
              position: "relative",
              "td:first-of-type:before": {
                borderLeft: `6px solid ${borderColor}`,
                content: `""`,
                display: "block",
                width: "10px",
                height: "100%",
                left: 0,
                top: 0,
                borderRadius: "6px 0 0 6px",
                position: "absolute",
              },
            },
          }
        : {};
    },
    [borderColor]
  );
};
