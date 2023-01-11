import Head from "next/head";
import { Container } from "src/components/Container";
import { LoadingScreen } from "src/components/Loading/LoadingScreen";
import { Task } from "src/components/Tasks/Task";
import { useRankPrompterRepliesTask } from "src/hooks/tasks/useRankReplies";

const RankUserReplies = () => {
  const { tasks, isLoading, reset, trigger } = useRankPrompterRepliesTask();

  if (isLoading) {
    return <LoadingScreen text="Loading..." />;
  }

  if (tasks.length === 0) {
    return <Container className="p-6 text-center">No tasks found...</Container>;
  }

  return (
    <>
      <Head>
        <title>Rank User Replies</title>
        <meta name="description" content="Rank User Replies." />
      </Head>
      <Task key={tasks[0].task.id} frontendId={tasks[0].id} task={tasks[0].task} trigger={trigger} mutate={reset} />
    </>
  );
};

export default RankUserReplies;
