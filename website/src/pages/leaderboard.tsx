import { Box, Heading } from "@chakra-ui/react";
import Head from "next/head";
import { getDashboardLayout } from "src/components/Layout";
import { LeaderboardGridCell } from "src/components/LeaderboardGridCell";

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
        <LeaderboardGridCell />
      </Box>
    </>
  );
};

Leaderboard.getLayout = getDashboardLayout;

export default Leaderboard;
