import { Flex } from "@chakra-ui/react";
import Head from "next/head";
import { useTranslation } from "next-i18next";
import { useEffect, useMemo, useState } from "react";
import { LeaderboardWidget, TaskOption, WelcomeCard } from "src/components/Dashboard";
import { getDashboardLayout } from "src/components/Layout";
import { get } from "src/lib/api";
import { AvailableTasks, TaskCategory } from "src/types/Task";
export { getDefaultStaticProps as getStaticProps } from "src/lib/default_static_props";
import { TaskCategoryItem } from "src/components/Dashboard/TaskOption";
import useSWR from "swr";

const Dashboard = () => {
  // Adding a demonstrative call to the backend that includes the web's JWT.
  // TODO: add CORS headers to the python backend
  useSWR(`${process.env.NEXT_PUBLIC_BACKEND_URL}/api/v1/auth/check`, get);

  const {
    t,
    i18n: { language },
  } = useTranslation(["dashboard", "common", "tasks"]);
  const [activeLang, setLang] = useState<string>(null);
  const { data, mutate: fetchTasks } = useSWR<AvailableTasks>("/api/available_tasks", get, {
    refreshInterval: 2 * 60 * 1000, //2 minutes
    revalidateOnMount: false, // triggered in the hook below
  });

  useEffect(() => {
    // re-fetch tasks if the language has changed
    if (activeLang !== language) {
      setLang(language);
      fetchTasks();
    }
  }, [activeLang, setLang, language, fetchTasks]);

  const availableTaskTypes = useMemo(() => {
    const taskTypes = filterAvailableTasks(data ?? {});
    return { [TaskCategory.Random]: taskTypes };
  }, [data]);

  return (
    <>
      <Head>
        <title>{`${t("dashboard")} - ${t("common:title")}`}</title>
        <meta name="description" content="Chat with Open Assistant and provide feedback." key="description" />
      </Head>
      <Flex direction="column" gap="10">
        <WelcomeCard />
        <TaskOption content={availableTaskTypes} />
        <LeaderboardWidget />
      </Flex>
    </>
  );
};

Dashboard.getLayout = getDashboardLayout;

export default Dashboard;

const filterAvailableTasks = (availableTasks: Partial<AvailableTasks>) =>
  Object.entries(availableTasks)
    .filter(([, count]) => count > 0)
    .sort((a, b) => b[1] - a[1])
    .map(([taskType, count]) => ({ taskType, count })) as TaskCategoryItem[];
