import { CircularProgress } from "@chakra-ui/react";
import { createColumnHelper } from "@tanstack/react-table";
import { useTranslation } from "next-i18next";
import React, { useMemo } from "react";
import { get } from "src/lib/api";
import { LeaderboardEntity, LeaderboardReply, LeaderboardTimeFrame } from "src/types/Leaderboard";
import useSWRImmutable from "swr/immutable";

import { DataTable } from "../DataTable";

const columnHelper = createColumnHelper<LeaderboardEntity>();

/**
 * Presents a grid of leaderboard entries with more detailed information.
 */
export const LeaderboardTable = ({ timeFrame, limit }: { timeFrame: LeaderboardTimeFrame; limit: number }) => {
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

  if (isLoading) {
    return <CircularProgress isIndeterminate></CircularProgress>;
  }

  if (error) {
    return <span>Unable to load leaderboard</span>;
  }

  return <DataTable data={reply.leaderboard} columns={columns} caption={lastUpdated}></DataTable>;
};
