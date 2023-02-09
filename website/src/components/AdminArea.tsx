import { useRouter } from "next/router";
import { useSession } from "next-auth/react";
import { ReactNode, useEffect } from "react";

export const AdminArea = ({ children }: { children: ReactNode }) => {
  const router = useRouter();
  const { data: session, status } = useSession();

  useEffect(() => {
    if (status === "loading") {
      return;
    }
    if (session?.user.role === "admin") {
      return;
    }
    router.push("/");
  }, [router, session, status]);
  return <main>{status === "loading" ? "loading..." : children}</main>;
};
