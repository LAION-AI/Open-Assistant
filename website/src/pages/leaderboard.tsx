import { Box, Heading, Tab, TabList, TabPanel, TabPanels, Tabs } from "@chakra-ui/react";
import Head from "next/head";
import { getDashboardLayout } from "src/components/Layout";
import { LeaderboardGridCell } from "src/components/LeaderboardGridCell";
import { LeaderboardTimeFrame } from "src/types/Leaderboard";

const Leaderboard = () => {
  return (
    <>
      <Head>
        <title>Leaderboard - Open Assistant</title>
        <meta name="description" content="Leaderboard Rankings" charSet="UTF-8" />
      </Head>
      <Box display="flex" flexDirection="column">
        <Heading fontSize="2xl" fontWeight="bold" pb="4">
          Leaderboard
        </Heading>
        <Tabs isFitted isLazy>
          <TabList>
            <Tab>Daily</Tab>
            <Tab>Weekly</Tab>
            <Tab>Monthly</Tab>
            <Tab>Overall</Tab>
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
      </Box>
    </>
  );
};

Leaderboard.getLayout = getDashboardLayout;

export default Leaderboard;
