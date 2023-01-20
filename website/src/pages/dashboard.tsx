import { Flex } from "@chakra-ui/react";
import Head from "next/head";
import { LeaderboardTable, TaskOption, WelcomeCard } from "src/components/Dashboard";
import { getDashboardLayout } from "src/components/Layout";
import { TaskCategory } from "src/components/Tasks/TaskTypes";
export { getDefaultStaticProps as getStaticProps } from "src/lib/default_static_props";

const Dashboard = () => {
  return (
    <>
      <Head>
        <title>Dashboard - Open Assistant</title>
        <meta name="description" content="Chat with Open Assistant and provide feedback." />
      </Head>
      <Flex direction="column" gap="10">
        <WelcomeCard />
        <TaskOption displayTaskCategories={[TaskCategory.Tasks]} />
        <LeaderboardTable />
      </Flex>
    </>
  );
};

Dashboard.getLayout = (page) => getDashboardLayout(page);

export default Dashboard;
