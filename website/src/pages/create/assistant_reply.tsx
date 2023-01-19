import Head from "next/head";
import { serverSideTranslations } from "next-i18next/serverSideTranslations";
import { TaskEmptyState } from "src/components/EmptyState";
import { getDashboardLayout } from "src/components/Layout";
import { LoadingScreen } from "src/components/Loading/LoadingScreen";
import { Task } from "src/components/Tasks/Task";
import { useCreateAssistantReply } from "src/hooks/tasks/useCreateReply";

const AssistantReply = () => {
  const { tasks, isLoading, reset, trigger } = useCreateAssistantReply();

  if (isLoading) {
    return <LoadingScreen text="Loading..." />;
  }

  if (tasks.length === 0) {
    return <TaskEmptyState />;
  }

  return (
    <>
      <Head>
        <title>Reply as Assistant</title>
        <meta name="description" content="Reply as Assistant." />
      </Head>
      <Task key={tasks[0].task.id} frontendId={tasks[0].id} task={tasks[0].task} trigger={trigger} mutate={reset} />
    </>
  );
};

AssistantReply.getLayout = getDashboardLayout;

export const getStaticProps = async ({ locale }) => ({
  props: {
    ...(await serverSideTranslations(locale, ["common"])),
  },
});

export default AssistantReply;
