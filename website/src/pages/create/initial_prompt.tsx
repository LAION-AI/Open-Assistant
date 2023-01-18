import Head from "next/head";
import { TaskEmptyState } from "src/components/EmptyState";
import { getDashboardLayout } from "src/components/Layout";
import { LoadingScreen } from "src/components/Loading/LoadingScreen";
import { Task } from "src/components/Tasks/Task";
import { useCreateInitialPrompt } from "src/hooks/tasks/useCreateReply";

const InitialPrompt = () => {
  const { tasks, isLoading, reset, trigger } = useCreateInitialPrompt();

  if (isLoading) {
    return <LoadingScreen text="Loading..." />;
  }

  if (tasks.length === 0) {
    return <TaskEmptyState />;
  }

  return (
    <>
      <Head>
        <title>Initial Prompt</title>
        <meta name="description" content="Add an initial Prompt." />
      </Head>
      <Task key={tasks[0].task.id} frontendId={tasks[0].id} task={tasks[0].task} trigger={trigger} mutate={reset} />
    </>
  );
};

InitialPrompt.getLayout = getDashboardLayout;

export default InitialPrompt;
