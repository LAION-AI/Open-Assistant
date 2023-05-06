import { Button, Card, CardBody, Flex, Heading } from "@chakra-ui/react";
import Head from "next/head";
import { useTranslation } from "next-i18next";
import { useMemo } from "react";
import { LeaderboardWidget, TaskOption, WelcomeCard } from "src/components/Dashboard";
import { DashboardLayout } from "src/components/Layout";
import { get } from "src/lib/api";
import { AvailableTasks, TaskCategory } from "src/types/Task";
export { getDefaultServerSideProps as getStaticProps } from "src/lib/defaultServerSideProps";
import Link from "next/link";
import { XPBar } from "src/components/Account/XPBar";
import { TaskCategoryItem } from "src/components/Dashboard/TaskOption";
import { useBrowserConfig } from "src/hooks/env/BrowserEnv";
import { useCurrentLocale } from "src/hooks/locale/useCurrentLocale";
import { API_ROUTES } from "src/lib/routes";
import useSWR from "swr";

const Dashboard = () => {
  const { t } = useTranslation(["dashboard", "common", "tasks"]);
  const { ENABLE_CHAT } = useBrowserConfig();
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
        {ENABLE_CHAT && (
          <Flex direction="column" gap={4}>
            <Heading size="lg">{t("index:try_our_assistant")}</Heading>
            <Link href="/chat" aria-label="Chat">
              <Button variant="solid" colorScheme="blue" px={5} py={6}>
                {t("index:try_our_assistant")}
              </Button>
            </Link>
          </Flex>
        )}

        <TaskOption content={availableTaskTypes} />
        <Card>
          <CardBody>
            <XPBar />
          </CardBody>
        </Card>
        <LeaderboardWidget />
      </Flex>
    </>
  );
};

Dashboard.getLayout = DashboardLayout;

export default Dashboard;

const filterAvailableTasks = (availableTasks: Partial<AvailableTasks>) =>
  Object.entries(availableTasks)
    .filter(([, count]) => count > 0)
    .sort((a, b) => b[1] - a[1])
    .map(([taskType, count]) => ({ taskType, count })) as TaskCategoryItem[];
