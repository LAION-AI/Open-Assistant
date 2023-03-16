import { Flex } from "@chakra-ui/react";
import Head from "next/head";
import { useTranslation } from "next-i18next";
import { useMemo } from "react";
import { LeaderboardWidget, TaskOption, WelcomeCard } from "src/components/Dashboard";
import { getDashboardLayout } from "src/components/Layout";
import { get } from "src/lib/api";
import { AvailableTasks, TaskCategory } from "src/types/Task";
export { getDefaultStaticProps as getStaticProps } from "src/lib/default_static_props";
import { TaskCategoryItem } from "src/components/Dashboard/TaskOption";
import { useCurrentLocale } from "src/hooks/locale/useCurrentLocale";
import { API_ROUTES } from "src/lib/routes";
import useSWR from "swr";

const Dashboard = () => {
  const { t } = useTranslation(["dashboard", "common", "tasks"]);
  const lang = useCurrentLocale();
  const { data } = useSWR<AvailableTasks>(API_ROUTES.AVAILABLE_TASK({ lang }), get, {
    refreshInterval: 2 * 60 * 1000, //2 minutes
  });

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
