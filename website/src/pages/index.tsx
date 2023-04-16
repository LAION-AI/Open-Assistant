import { Box } from "@chakra-ui/react";
import Head from "next/head";
import { useRouter } from "next/router";
import { useSession } from "next-auth/react";
import { useTranslation } from "next-i18next";
import { useEffect } from "react";
import { CallToAction } from "src/components/CallToAction";
import { Faq } from "src/components/Faq";
import { Hero } from "src/components/Hero";
export { getDefaultServerSideProps as getStaticProps } from "src/lib/defaultServerSideProps";

const Home = () => {
  const router = useRouter();
  const { status } = useSession();
  const { t } = useTranslation();
  useEffect(() => {
    if (status === "authenticated") {
      router.push("/dashboard");
    }
  }, [router, status]);

  return (
    <>
      <Head>
        <title>{t("title")}</title>
      </Head>
      <Box as="main" className="oa-basic-theme">
        <Hero />
        <CallToAction />
        <Faq />
      </Box>
    </>
  );
};

export default Home;
