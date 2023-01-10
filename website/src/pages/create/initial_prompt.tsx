import { Container } from "@chakra-ui/react";
import Head from "next/head";
import { LoadingScreen } from "src/components/Loading/LoadingScreen";
import { Task } from "src/components/Tasks/Task";
import { useCreateInitialPrompt } from "src/hooks/tasks/useCreateReply";

const InitialPrompt = () => {
  const { tasks, isLoading, reset, trigger } = useCreateInitialPrompt();

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
      <Task key={tasks[0].task.id} task={tasks[0].task} trigger={trigger} mutate={reset} />
    </>
  );
};

export default InitialPrompt;
