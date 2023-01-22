import { Flex } from "@chakra-ui/react";
import Head from "next/head";
import { useMemo } from "react";
import { LeaderboardTable, TaskOption, WelcomeCard } from "src/components/Dashboard";
import { getDashboardLayout } from "src/components/Layout";
import { TaskCategory } from "src/components/Tasks/TaskTypes";
import { get } from "src/lib/api";
import { AvailableTasks, TaskType } from "src/types/Task";
export { getDefaultStaticProps as getStaticProps } from "src/lib/default_static_props";
import useSWRImmutable from "swr/immutable";

const Dashboard = () => {
  const { data } = useSWRImmutable<AvailableTasks>("/api/available_tasks", get);

  const availableTaskTypes = useMemo(() => {
    const taskTypes = filterAvailableTasks(data ?? {});
    return { [TaskCategory.Random]: taskTypes };
  }, [data]);

  return (
    <>
      <Head>
        <title>Dashboard - Open Assistant</title>
        <meta name="description" content="Chat with Open Assistant and provide feedback." />
      </Head>
      <Flex direction="column" gap="10">
        <WelcomeCard />
        <TaskOption content={availableTaskTypes} />
        <LeaderboardTable />
      </Flex>
    </>
  );
};

Dashboard.getLayout = getDashboardLayout;

export default Dashboard;

const filterAvailableTasks = (availableTasks: Partial<AvailableTasks>) =>
  Object.entries(availableTasks)
    .filter(([_, count]) => count > 0)
    .sort((a, b) => b[1] - a[1])
    .map(([taskType]) => taskType) as TaskType[];
