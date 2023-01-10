import { Container } from "@chakra-ui/react";
import Head from "next/head";
import { LoadingScreen } from "src/components/Loading/LoadingScreen";
import { Task } from "src/components/Tasks/Task";
import { useLabelInitialPromptTask } from "src/hooks/tasks/useLabelingTask";

const LabelInitialPrompt = () => {
  const { tasks, isLoading, trigger, reset } = useLabelInitialPromptTask();

  if (isLoading) {
    return <LoadingScreen />;
  }

  if (tasks.length === 0) {
    return <Container className="p-6 text-center text-gray-800">No tasks found...</Container>;
  }

  return (
    <>
      <Head>
        <title>Label Initial Prompt</title>
        <meta name="description" content="Label Initial Prompt" />
      </Head>
      <Task tasks={tasks} trigger={trigger} mutate={reset} />
    </>
  );
};

export default LabelInitialPrompt;
