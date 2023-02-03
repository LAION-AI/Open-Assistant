import { useCallback, useEffect, useState } from "react";
import { get, post } from "src/lib/api";
import useSWR, { useSWRConfig } from "swr";

export const useToSAcceptance = () => {
  const [hasAcceptedTos, setHasAccepted] = useState(false);
  const { data: acceptanceDate, mutate: refreshToSStatus } = useSWR<string | null>(
    hasAcceptedTos ? null : "/api/tos",
    get
  );

  useEffect(() => {
    if (typeof acceptanceDate === "string") {
      setHasAccepted(true);
    }
  }, [acceptanceDate]);

  const { mutate } = useSWRConfig();
  const acceptToS = useCallback(async () => {
    if (!hasAcceptedTos) {
      await mutate("/api/tos", post);
      await refreshToSStatus();
    }
  }, [hasAcceptedTos, mutate, refreshToSStatus]);

  return { hasAcceptedTos, acceptanceDate, acceptToS };
};
