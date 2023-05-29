import { useRouter } from "next/router";
import { useSession } from "next-auth/react";
import { ReactNode, useEffect } from "react";
import { SWRConfig, SWRConfiguration } from "swr";
const swrConfig: SWRConfiguration = {
  revalidateOnFocus: true,
  revalidateOnMount: true,
};

export const AdminArea = ({ children }: { children: ReactNode }) => {
  const router = useRouter();
  const { data: session, status } = useSession();

  useEffect(() => {
    if (status === "loading") {
      return;
    }
    const role = session?.user.role;

    if (role === "admin" || role === "moderator") {
      return;
    }

    router.push("/");
  }, [router, session, status]);

  return (
    <SWRConfig value={swrConfig}>
      <main>{status === "loading" ? "loading..." : children}</main>
    </SWRConfig>
  );
};
