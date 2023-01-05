import { Box, useColorMode } from "@chakra-ui/react";
import Head from "next/head";

import { getDashboardLayout } from "src/components/Layout";
import { LeaderboardTable, SideMenu, TaskOption } from "src/components/Dashboard";
import { colors } from "styles/Theme/colors";

const Dashboard = () => {
  const { colorMode } = useColorMode();
  return (
    <>
      <Head>
        <title>Dashboard - Open Assistant</title>
        <meta name="description" content="Chat with Open Assistant and provide feedback." />
      </Head>
      <Box backgroundColor={colorMode === "light" ? colors.light.bg : colors.dark.bg} className="sm:overflow-hidden">
        <Box className="sm:flex h-full gap-6">
          <Box className="p-6 sm:pr-0">
            <SideMenu />
          </Box>
          <Box className="flex flex-col overflow-auto p-6 sm:pl-0 gap-14">
            <TaskOption />
            <LeaderboardTable />
          </Box>
        </Box>
      </Box>
    </>
  );
};

Dashboard.getLayout = (page) => getDashboardLayout(page);

export default Dashboard;
