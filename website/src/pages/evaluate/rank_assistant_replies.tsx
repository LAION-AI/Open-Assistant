import Head from "next/head";
import { TaskEmptyState } from "src/components/EmptyState";
import { LoadingScreen } from "src/components/Loading/LoadingScreen";
import { Task } from "src/components/Tasks/Task";
import { useRankAssistantRepliesTask } from "src/hooks/tasks/useRankReplies";

const RankAssistantReplies = () => {
  const { tasks, isLoading, reset, trigger } = useRankAssistantRepliesTask();

  if (isLoading) {
    return <LoadingScreen text="Loading..." />;
  }

  if (tasks.length === 0) {
    return <TaskEmptyState />;
  }

  return (
    <>
      <Head>
        <title>Rank Assistant Replies</title>
        <meta name="description" content="Rank Assistant Replies." />
      </Head>
      <Task key={tasks[0].task.id} frontendId={tasks[0].id} task={tasks[0].task} trigger={trigger} mutate={reset} />
    </>
  );
};

export default RankAssistantReplies;
