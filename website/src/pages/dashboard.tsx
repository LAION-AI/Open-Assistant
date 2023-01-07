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
      <TaskOption />
      <LeaderboardTable />
    </>
  );
};

Dashboard.getLayout = (page) => getDashboardLayout(page);

export default Dashboard;
