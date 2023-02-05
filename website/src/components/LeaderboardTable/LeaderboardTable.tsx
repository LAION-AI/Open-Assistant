import { CircularProgress, useColorModeValue, useToken } from "@chakra-ui/react";
import { createColumnHelper } from "@tanstack/react-table";
import { useTranslation } from "next-i18next";
import React, { useCallback, useMemo, useState } from "react";
import { get } from "src/lib/api";
import { colors } from "src/styles/Theme/colors";
import { LeaderboardEntity, LeaderboardReply, LeaderboardTimeFrame } from "src/types/Leaderboard";
import useSWRImmutable from "swr/immutable";

import { DataTable, DataTableRowPropsCallback } from "../DataTable";

const columnHelper = createColumnHelper<LeaderboardEntity>();

/**
 * Presents a grid of leaderboard entries with more detailed information.
 */
export const LeaderboardTable = ({
  timeFrame,
  limit: limit,
  rowPerPage,
}: {
  timeFrame: LeaderboardTimeFrame;
  limit: number;
  rowPerPage: number;
}) => {
  const { t } = useTranslation("leaderboard");

  const {
    data: reply,
    isLoading,
    error,
  } = useSWRImmutable<LeaderboardReply>(`/api/leaderboard?time_frame=${timeFrame}&limit=${limit}`, get, {
    revalidateOnMount: true,
  });

  const columns = useMemo(
    () => [
      columnHelper.accessor("rank", {
        header: t("rank"),
      }),
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
  const data = useMemo(() => {
    const start = (page - 1) * rowPerPage;
    return reply?.leaderboard.slice(start, start + rowPerPage) || [];
  }, [rowPerPage, page, reply?.leaderboard]);

  const borderColor = useToken("colors", useColorModeValue(colors.light.active, colors.dark.active));
  const rowProps = useCallback<DataTableRowPropsCallback<LeaderboardEntity>>(
    (row) => {
      return row.original.highlighted
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
      disableNext={page === maxPage}
      disablePrevious={page === 1}
      onNextClick={() => setPage((p) => p + 1)}
      onPreviousClick={() => setPage((p) => p - 1)}
      rowProps={rowProps}
    ></DataTable>
  );
};
