import { Button, Card, CardBody, Flex, Heading } from "@chakra-ui/react";
import Head from "next/head";
import { useRouter } from "next/router";
import { useTranslation } from "next-i18next";
import { useEffect, useMemo } from "react";
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
  const { ENABLE_CHAT, BYE } = useBrowserConfig();
  const router = useRouter();
  const lang = useCurrentLocale();
  const { data } = useSWR<AvailableTasks>(API_ROUTES.AVAILABLE_TASK({ lang }), get, {
    refreshInterval: 2 * 60 * 1000, //2 minutes
  });

  const availableTaskTypes = useMemo(() => {
    const taskTypes = filterAvailableTasks(data ?? {});
    return { [TaskCategory.Random]: taskTypes };
  }, [data]);

  const chatButtonStyle = {
    position: "relative",
    display: "inline-block",
    backgroundColor: "blue.500",
    color: "white",
    padding: "0.5em 1em",
    boxShadow: "0 0.5em 1em rgba(0,0,0,0.2)",
    "&::before": {
      content: "''",
      position: "absolute",
      top: "100%",
      left: "1.25em",
      width: 0,
      height: 0,
      borderTop: "-1.25em solid transparent",
      borderBottom: "1.25em solid transparent",
      borderLeft: "1.25em solid #3182CE",
      transition: "all 0.3s ease-in-out",
    },
    "&:hover": {
      backgroundColor: "blue.600",
      "&::before": {
        borderLeft: "1.25em solid #2b6cb0",
      },
    },
  };

  useEffect(() => {
    if (BYE) {
      router.push("/bye");
    }
  }, [BYE, router]);

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
            <Link href="/chat" aria-label="Chat" style={{ width: "max-content" }}>
              <Button sx={chatButtonStyle}>{t("index:chat_with_our_assistant")}</Button>
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
