import { Container } from "@chakra-ui/react";
import Head from "next/head";
import { useEffect } from "react";
import { LoadingScreen } from "src/components/Loading/LoadingScreen";
import { Task } from "src/components/Tasks/Task";
import { useGenericTaskAPI } from "src/hooks/tasks/useGenericTaskAPI";

const RandomTask = () => {
  const { tasks, isLoading, trigger, reset } = useGenericTaskAPI("random");

  useEffect(() => {
    if (tasks.length == 0) {
      reset();
    }
  }, [tasks]);

  if (isLoading) {
    return <LoadingScreen text="Loading..." />;
  }

  if (tasks.length == 0) {
    return <Container className="p-6 text-center text-gray-800">No tasks found...</Container>;
  }

  return (
    <>
      <Head>
        <title>Random Task</title>
        <meta name="description" content="Random Task." />
      </Head>
      <Task tasks={tasks} trigger={trigger} mutate={reset} />
    </>
  );
};

export default RandomTask;
