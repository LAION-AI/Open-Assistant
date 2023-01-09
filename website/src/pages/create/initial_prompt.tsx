import { Container } from "@chakra-ui/react";
import { useColorMode } from "@chakra-ui/react";
import Head from "next/head";
import { LoadingScreen } from "src/components/Loading/LoadingScreen";
import { Task } from "src/components/Tasks/Task";
import { useCreateInitialPrompt } from "src/hooks/tasks/create/useCreateInitialPrompt";

const InitialPrompt = () => {
  const { tasks, isLoading, reset, trigger } = useCreateInitialPrompt();

  const { colorMode } = useColorMode();
  const mainBgClasses = colorMode === "light" ? "bg-slate-300 text-gray-800" : "bg-slate-900 text-white";

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
      <Task tasks={tasks} trigger={trigger} mutate={reset} mainBgClasses={mainBgClasses} />
    </>
  );
};

export default InitialPrompt;
