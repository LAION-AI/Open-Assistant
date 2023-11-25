import { useRouter } from "next/router";
import { useEffect } from "react";

const ContributorsPage = () => {
  const router = useRouter();
  useEffect(() => {
    router.push("https://ykilcher.com/oa-contributors");
  }, [router]);

  return null;
};

export default ContributorsPage;
