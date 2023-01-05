import { useColorMode } from "@chakra-ui/react";
import Head from "next/head";
import { useEffect, useState } from "react";
import { LoadingScreen } from "src/components/Loading/LoadingScreen";
import { Sortable } from "src/components/Sortable/Sortable";
import { SurveyCard } from "src/components/Survey/SurveyCard";
import { TaskControls } from "src/components/Survey/TaskControls";
import fetcher from "src/lib/fetcher";
import poster from "src/lib/poster";
import useSWRImmutable from "swr/immutable";
import useSWRMutation from "swr/mutation";

const RankInitialPrompts = () => {
  const [tasks, setTasks] = useState([]);
  /**
   * This array will contain the ranked indices of the prompts
   * The best prompt will have index 0, and the worst is the last.
   */
  const [ranking, setRanking] = useState<number[]>([]);
  // const bg = useColorModeValue("gray.100", "gray.800");

  const { isLoading, mutate } = useSWRImmutable("/api/new_task/rank_initial_prompts", fetcher, {
    onSuccess: (data) => {
      setTasks([data]);
    },
  });

  const { trigger } = useSWRMutation("/api/update_task", poster, {
    onSuccess: async (data) => {
      const newTask = await data.json();
      setTasks((oldTasks) => [...oldTasks, newTask]);
    },
  });

  useEffect(() => {
    if (tasks.length == 0) {
      mutate();
    }
  }, [tasks]);

  const submitResponse = (task) => {
    trigger({
      id: task.id,
      update_type: "message_ranking",
      content: {
        ranking,
      },
    });
  };

  const fetchNextTask = () => {
    setRanking([]);
    mutate();
  };

  const { colorMode } = useColorMode();
  const mainBgClasses = colorMode === "light" ? "bg-slate-300 text-gray-800" : "bg-slate-900 text-white";

  if (isLoading) {
    return <LoadingScreen text="Loading..." />;
  }

  if (tasks.length == 0) {
    return (
      <div className={`p-12 ${mainBgClasses}`}>
        <div className="flex h-full">
          <div className="text-xl font-bold  mx-auto my-auto">No tasks found...</div>
        </div>
      </div>
    );
  }

  return (
    <>
      <Head>
        <title>Rank Initial Prompts</title>
        <meta name="description" content="Rank initial prompts." />
      </Head>
      <div className={`p-12 ${mainBgClasses}`}>
        <SurveyCard className="max-w-7xl mx-auto h-fit mb-24">
          <h5 className="text-lg font-semibold mb-4">Instructions</h5>
          <p className="text-lg py-1">
            Given the following prompts, sort them from best to worst, best being first, worst being last.
          </p>
          <Sortable items={tasks[0].task.prompts} onChange={setRanking} className="my-8" />
        </SurveyCard>

        <TaskControls tasks={tasks} onSubmitResponse={submitResponse} onSkip={fetchNextTask} />
      </div>
    </>
  );
};

export default RankInitialPrompts;
