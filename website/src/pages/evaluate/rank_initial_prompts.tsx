import { useColorMode } from "@chakra-ui/react";
import Head from "next/head";
import { Container } from "src/components/Container";
import { LoadingScreen } from "src/components/Loading/LoadingScreen";
import { Task } from "src/components/Tasks/Task";
import { useRankInitialPromptsTask } from "src/hooks/tasks/evaluate/useRankInitialPrompts";

const RankInitialPrompts = () => {
  const { tasks, isLoading, reset, trigger } = useRankInitialPromptsTask();

  const { colorMode } = useColorMode();
  const mainBgClasses = colorMode === "light" ? "bg-slate-300 text-gray-800" : "bg-slate-900 text-white";

  if (isLoading) {
    return <LoadingScreen text="Loading..." />;
  }

  if (tasks.length === 0) {
    return <Container className="p-6 text-center">No tasks found...</Container>;
  }

  return (
    <>
      <Head>
        <title>Rank Initial Prompts</title>
        <meta name="description" content="Rank initial prompts." />
      </Head>
      <Task tasks={tasks} trigger={trigger} mutate={reset} mainBgClasses={mainBgClasses} />
    </>
  );
};

export default RankInitialPrompts;
