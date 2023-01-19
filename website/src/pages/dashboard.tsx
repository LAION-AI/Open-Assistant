import { Flex } from "@chakra-ui/react";
import Head from "next/head";
import { serverSideTranslations } from "next-i18next/serverSideTranslations";
import { LeaderboardTable, TaskOption, WelcomeCard } from "src/components/Dashboard";
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
        <WelcomeCard />
        <TaskOption displayTaskCategories={[TaskCategory.Tasks]} />
        <LeaderboardTable />
      </Flex>
    </>
  );
};

Dashboard.getLayout = (page) => getDashboardLayout(page);

export const getStaticProps = async ({ locale }) => ({
  props: {
    ...(await serverSideTranslations(locale, ["common"])),
  },
});

export default Dashboard;
