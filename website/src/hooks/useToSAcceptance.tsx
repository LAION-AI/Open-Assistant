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

const useToSAcceptance = (): ToSContextType => {
  const [hasAcceptedTos, setHasAccepted] = useState(false);

  const { data: session } = useSession();
  const isLoggedIn = Boolean(session);
  const shouldFetchToS = isLoggedIn && !hasAcceptedTos;

  const { data: acceptanceDate, mutate: refreshToSStatus } = useSWR<string | null>(
    shouldFetchToS ? "/api/tos" : null,
    get
  );

  useEffect(() => {
    if (typeof acceptanceDate === "string") {
      setHasAccepted(true);
    }
  }, [acceptanceDate]);

  const acceptToS = useCallback(async () => {
    if (!hasAcceptedTos) {
      await post("/api/tos", { arg: {} });
      await refreshToSStatus();
    }
  }, [hasAcceptedTos, refreshToSStatus]);

  return { hasAcceptedTos, acceptanceDate, acceptToS };
};

export const ToSProvider = ({ children }) => {
  const tosAcceptance = useToSAcceptance();
  return <TosContext.Provider value={tosAcceptance}>{children}</TosContext.Provider>;
};
