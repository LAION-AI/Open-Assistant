import Head from "next/head";
import { useTranslation } from "next-i18next";
import { DashboardLayout } from "src/components/Layout";
import { Stats } from "src/components/Stats";
import { get } from "src/lib/api";
import { Stats as StatsType } from "src/types/Stat";
export { getStaticProps } from "src/lib/defaultServerSideProps";
import uswSWRImmutable from "swr/immutable";

const StatsPage = () => {
  const { data } = uswSWRImmutable<StatsType>("/api/stats/cached_stats", get);
  const { t } = useTranslation();
  const title = `${t("stats")} - ${t("title")}`;

  return (
    <>
      <Head>
        <title>{title}</title>
        <meta name="description" content="Open Assistant Stats" />
      </Head>
      <Stats data={data} />
    </>
  );
};

StatsPage.getLayout = DashboardLayout;

export default StatsPage;
