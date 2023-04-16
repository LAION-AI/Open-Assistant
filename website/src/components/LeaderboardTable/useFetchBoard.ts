import { useTranslation } from "next-i18next";
import { useMemo } from "react";
import { get } from "src/lib/api";
import useSWRImmutable from "swr/immutable";

export const useFetchBoard = <T extends { last_updated: string }>(url: string) => {
  const { t } = useTranslation("leaderboard");
  const res = useSWRImmutable<T>(url, get);

  const lastUpdated = useMemo(() => {
    const val = res.data ? new Date(res.data.last_updated) : new Date();
    return t("last_updated_at", { val, formatParams: { val: { dateStyle: "full", timeStyle: "short" } } });
  }, [res.data, t]);

  return {
    ...res,
    lastUpdated,
  };
};
