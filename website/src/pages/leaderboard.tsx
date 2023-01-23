import { Box, Card, CardBody, Heading, Tab, TabList, TabPanel, TabPanels, Tabs } from "@chakra-ui/react";
import Head from "next/head";
import { useTranslation } from "next-i18next";
import { getDashboardLayout } from "src/components/Layout";
import { LeaderboardGridCell } from "src/components/LeaderboardGridCell";
export { getDefaultStaticProps as getStaticProps } from "src/lib/default_static_props";
import { LeaderboardTimeFrame } from "src/types/Leaderboard";

const Leaderboard = () => {
  const { t } = useTranslation(["leaderboard", "common"]);
  return (
    <>
      <Head>
        <title>{`${t("leaderboard:leaderboard")} - ${t("common:title")}`}</title>
        <meta name="description" content="Leaderboard Rankings" charSet="UTF-8" />
      </Head>
      <Box display="flex" flexDirection="column">
        <Heading fontSize="2xl" fontWeight="bold" pb="4">
          {t("leaderboard:leaderboard")}
        </Heading>
        <Card>
          <CardBody>
            <Tabs isFitted isLazy>
              <TabList>
                <Tab>{t("leaderboard:daily")}</Tab>
                <Tab>{t("leaderboard:weekly")}</Tab>
                <Tab>{t("leaderboard:monthly")}</Tab>
                <Tab>{t("leaderboard:overall")}</Tab>
              </TabList>

              <TabPanels>
                <TabPanel p="0">
                  <LeaderboardGridCell timeFrame={LeaderboardTimeFrame.day} />
                </TabPanel>
                <TabPanel p="0">
                  <LeaderboardGridCell timeFrame={LeaderboardTimeFrame.week} />
                </TabPanel>
                <TabPanel p="0">
                  <LeaderboardGridCell timeFrame={LeaderboardTimeFrame.month} />
                </TabPanel>
                <TabPanel p="0">
                  <LeaderboardGridCell timeFrame={LeaderboardTimeFrame.total} />
                </TabPanel>
              </TabPanels>
            </Tabs>
          </CardBody>
        </Card>
      </Box>
    </>
  );
};

Leaderboard.getLayout = getDashboardLayout;

export default Leaderboard;
