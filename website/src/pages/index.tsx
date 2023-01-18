import { Box } from "@chakra-ui/react";
import Head from "next/head";
import { useRouter } from "next/router";
import { useSession } from "next-auth/react";
import { useTranslation } from "next-i18next";
import { serverSideTranslations } from "next-i18next/serverSideTranslations";
import { useEffect } from "react";
import { CallToAction } from "src/components/CallToAction";
import { Faq } from "src/components/Faq";
import { Hero } from "src/components/Hero";
import { getTransparentHeaderLayout } from "src/components/Layout";

const Home = () => {
  const router = useRouter();
  const { status } = useSession();
  const { t } = useTranslation("index");
  useEffect(() => {
    if (status === "authenticated") {
      router.push("/dashboard");
    }
  }, [router, status]);

  return (
    <>
      <Head>
        <title>{t("title")}</title>
        <meta name="description" content={t("description")} />
      </Head>
      <Box as="main" className="oa-basic-theme">
        <Hero />
        <CallToAction />
        <Faq />
      </Box>
    </>
  );
};

Home.getLayout = getTransparentHeaderLayout;

export const getStaticProps = async ({ locale }) => ({
  props: {
    ...(await serverSideTranslations(locale, ["index", "common"])),
  },
});

export default Home;
