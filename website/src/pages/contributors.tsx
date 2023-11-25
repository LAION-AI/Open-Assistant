import { useRouter } from "next/router";

const ContributorsPage = () => {
  const router = useRouter();
  router.push("https://ykilcher.com/oa-contributors");
  return null;
};

export default ContributorsPage;
