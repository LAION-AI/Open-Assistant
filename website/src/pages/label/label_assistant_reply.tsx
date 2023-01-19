import Head from "next/head";
import { serverSideTranslations } from "next-i18next/serverSideTranslations";
import { TaskEmptyState } from "src/components/EmptyState";
import { getDashboardLayout } from "src/components/Layout";
import { LoadingScreen } from "src/components/Loading/LoadingScreen";
import { Task } from "src/components/Tasks/Task";
import { useLabelAssistantReplyTask } from "src/hooks/tasks/useLabelingTask";

const LabelAssistantReply = () => {
  const { tasks, isLoading, trigger, reset } = useLabelAssistantReplyTask();

  if (isLoading) {
    return <LoadingScreen />;
  }

  if (tasks.length === 0) {
    return <TaskEmptyState />;
  }

  return (
    <>
      <Head>
        <title>Label Assistant Reply</title>
        <meta name="description" content="Label Assistant Reply" />
      </Head>
      <Task key={tasks[0].task.id} frontendId={tasks[0].id} task={tasks[0].task} trigger={trigger} mutate={reset} />
    </>
  );
};

LabelAssistantReply.getLayout = getDashboardLayout;

export const getStaticProps = async ({ locale }) => ({
  props: {
    ...(await serverSideTranslations(locale, ["common"])),
  },
});

export default LabelAssistantReply;
