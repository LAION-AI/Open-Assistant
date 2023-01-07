import { Box } from "@chakra-ui/react";
import Head from "next/head";

import { getDashboardLayout } from "src/components/Layout";
import { LeaderboardTable, TaskOption } from "src/components/Dashboard";

const Dashboard = () => {
  return (
    <>
      <Head>
        <title>Dashboard - Open Assistant</title>
        <meta name="description" content="Chat with Open Assistant and provide feedback." />
      </Head>
      <Box className="flex flex-col overflow-auto p-6 sm:pl-0 gap-14">
        <TaskOption />
        <LeaderboardTable />
      </Box>
    </>
  );
};

Dashboard.getLayout = (page) => getDashboardLayout(page);

export default Dashboard;
