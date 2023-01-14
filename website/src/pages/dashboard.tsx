import { Flex } from "@chakra-ui/react";
import Head from "next/head";
import { LeaderboardTable, TaskOption, WelcomeModal } from "src/components/Dashboard";
import { getDashboardLayout } from "src/components/Layout";
import { TaskCategory } from "src/components/Tasks/TaskTypes";

const Dashboard = () => {
  return (
    <>
      <Head>
        <title>Dashboard - Open Assistant</title>
        <meta name="description" content="Chat with Open Assistant and provide feedback." />
      </Head>
      <Flex direction="column" gap="10">
        <WelcomeModal />
        <TaskOption displayTaskCategories={[TaskCategory.Tasks]} />
        <LeaderboardTable />
      </Flex>
    </>
  );
};

Dashboard.getLayout = (page) => getDashboardLayout(page);

export default Dashboard;
