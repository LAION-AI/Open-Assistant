import Head from "next/head";
import { TaskEmptyState } from "src/components/EmptyState";
import { getDashboardLayout } from "src/components/Layout";
import { LoadingScreen } from "src/components/Loading/LoadingScreen";
import { Task } from "src/components/Tasks/Task";
import { useRankInitialPromptsTask } from "src/hooks/tasks/useRankReplies";

const RankInitialPrompts = () => {
  const { tasks, isLoading, reset, trigger } = useRankInitialPromptsTask();

  if (isLoading) {
    return <LoadingScreen text="Loading..." />;
  }

  if (tasks.length === 0) {
    return <TaskEmptyState />;
  }

  return (
    <>
      <Head>
        <title>Rank Initial Prompts</title>
        <meta name="description" content="Rank initial prompts." />
      </Head>
      <Task key={tasks[0].task.id} frontendId={tasks[0].id} task={tasks[0].task} trigger={trigger} mutate={reset} />
    </>
  );
};

RankInitialPrompts.getLayout = getDashboardLayout;

export default RankInitialPrompts;
