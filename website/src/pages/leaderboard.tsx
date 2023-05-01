import { Box, Card, CardBody, Heading, Tab, TabList, TabPanel, TabPanels, Tabs } from "@chakra-ui/react";
import Head from "next/head";
import { useTranslation } from "next-i18next";
import { DashboardLayout } from "src/components/Layout";
export { getStaticProps } from "src/lib/defaultServerSideProps";
import { LeaderboardTable } from "src/components/LeaderboardTable";
import { LeaderboardTimeFrame } from "src/types/Leaderboard";

const Leaderboard = () => {
  const { t } = useTranslation(["leaderboard", "common"]);
  return (
    <>
      <Head>
        <title>{`${t("leaderboard")} - ${t("common:title")}`}</title>
        <meta name="description" content="Leaderboard Rankings" charSet="UTF-8" />
      </Head>
      <Box display="flex" flexDirection="column">
        <Heading fontSize="2xl" fontWeight="bold" pb="4">
          {t("leaderboard")}
        </Heading>
        <Card>
          <CardBody>
            <Tabs isFitted isLazy>
              <TabList mb={4}>
                <Tab>{t("daily")}</Tab>
                <Tab>{t("weekly")}</Tab>
                <Tab>{t("monthly")}</Tab>
                <Tab>{t("overall")}</Tab>
              </TabList>
              <TabPanels>
                <TabPanel p="0">
                  <LeaderboardTable timeFrame={LeaderboardTimeFrame.day} limit={100} rowPerPage={20} />
                </TabPanel>
                <TabPanel p="0">
                  <LeaderboardTable timeFrame={LeaderboardTimeFrame.week} limit={100} rowPerPage={20} />
                </TabPanel>
                <TabPanel p="0">
                  <LeaderboardTable timeFrame={LeaderboardTimeFrame.month} limit={100} rowPerPage={20} />
                </TabPanel>
                <TabPanel p="0">
                  <LeaderboardTable timeFrame={LeaderboardTimeFrame.total} limit={100} rowPerPage={20} />
                </TabPanel>
              </TabPanels>
            </Tabs>
          </CardBody>
        </Card>
      </Box>
    </>
  );
};

Leaderboard.getLayout = DashboardLayout;

export default Leaderboard;
