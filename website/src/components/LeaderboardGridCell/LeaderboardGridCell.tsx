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
const LeaderboardGridCell = ({ timeFrame }: { timeFrame: LeaderboardTimeFrame }) => {
  const { t } = useTranslation("leaderboard");
  const {
    data: reply,
    isLoading,
    error,
  } = useSWRImmutable<LeaderboardReply>(`/api/leaderboard?time_frame=${timeFrame}`, get, {
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
        header: t("pro"),
      }),
    ],
    [t]
  );

  const lastUpdated = useMemo(() => {
    const val = new Date(reply?.last_updated);
    return t("last_updated_at", { val, formatParams: { val: { dateStyle: "full", timeStyle: "short" } } });
  }, [t, reply?.last_updated]);
  console.log(reply, isLoading);

  if (isLoading) {
    return <CircularProgress isIndeterminate></CircularProgress>;
  }

  if (error) {
    return <span>Unable to load leaderboard</span>;
  }

  return <DataTable data={reply?.leaderboard || []} columns={columns} caption={lastUpdated}></DataTable>;
};

export { LeaderboardGridCell };
