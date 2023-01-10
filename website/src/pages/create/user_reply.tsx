import Head from "next/head";
import { Container } from "src/components/Container";
import { LoadingScreen } from "src/components/Loading/LoadingScreen";
import { Task } from "src/components/Tasks/Task";
import { useCreatePrompterReply } from "src/hooks/tasks/useCreateReply";

const UserReply = () => {
  const { tasks, isLoading, reset, trigger } = useCreatePrompterReply();

  if (isLoading) {
    return <LoadingScreen text="Loading..." />;
  }

  if (tasks.length === 0) {
    return <Container className="p-6 text-center text-gray-800">No tasks found...</Container>;
  }

  return (
    <>
      <Head>
        <title>Reply as Assistant</title>
        <meta name="description" content="Reply as Assistant." />
      </Head>
      <Task tasks={tasks} trigger={trigger} mutate={reset} />
    </>
  );
};

export default UserReply;
