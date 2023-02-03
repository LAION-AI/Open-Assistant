import { useSession } from "next-auth/react";
import { createContext, useCallback, useEffect, useState } from "react";
import { get, post } from "src/lib/api";
import useSWR from "swr";

interface ToSContextType {
  hasAcceptedTos: boolean;
  acceptanceDate: string;
  acceptToS: () => Promise<void>;
}

export const TosContext = createContext<ToSContextType>(null);

const useToSAcceptance = (enabled: boolean): ToSContextType => {
  const [hasAcceptedTos, setHasAccepted] = useState(false);
  const { data: acceptanceDate, mutate: refreshToSStatus } = useSWR<string | null>(
    enabled && !hasAcceptedTos ? "/api/tos" : null,
    get
  );

  useEffect(() => {
    if (typeof acceptanceDate === "string") {
      setHasAccepted(true);
    }
  }, [acceptanceDate]);

  const acceptToS = useCallback(async () => {
    await post("/api/tos", { arg: {} });
    await refreshToSStatus();
  }, [refreshToSStatus]);

  return { hasAcceptedTos, acceptanceDate, acceptToS };
};

export const ToSProvider = ({ children }) => {
  const { data: session } = useSession();
  const isLoggedIn = Boolean(session);
  const tosAcceptance = useToSAcceptance(isLoggedIn);

  return <TosContext.Provider value={tosAcceptance}>{children}</TosContext.Provider>;
};
