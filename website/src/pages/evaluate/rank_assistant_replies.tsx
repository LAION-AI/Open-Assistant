import { Flex } from "@chakra-ui/react";
import Head from "next/head";
import { useState } from "react";
import { SkipButton } from "src/components/Buttons/Skip";
import { SubmitButton } from "src/components/Buttons/Submit";
import { LoadingScreen } from "src/components/Loading/LoadingScreen";
import { Sortable } from "src/components/Sortable/Sortable";
import { TaskInfo } from "src/components/TaskInfo/TaskInfo";
import fetcher from "src/lib/fetcher";
import poster from "src/lib/poster";
import useSWRImmutable from "swr/immutable";
import useSWRMutation from "swr/mutation";

const RankAssistantReplies = () => {
  const [tasks, setTasks] = useState([]);
  /**
   * This array will contain the ranked indices of the replies
   * The best reply will have index 0, and the worst is the last.
   */
  const [ranking, setRanking] = useState<number[]>([]);

  const { isLoading, mutate } = useSWRImmutable("/api/new_task/rank_assistant_replies", fetcher, {
    onSuccess: (data) => {
      setTasks([data]);
    },
  });

  const { trigger, isMutating } = useSWRMutation("/api/update_task", poster, {
    onSuccess: async (data) => {
      const newTask = await data.json();
      setTasks((oldTasks) => [...oldTasks, newTask]);
    },
  });

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

  if (isLoading) {
    return <LoadingScreen text="Loading..." />;
  }

  if (tasks.length == 0) {
    return <div className="p-6 bg-slate-100 text-gray-800">Loading...</div>;
  }

  const replies = tasks[0].task.replies as string[];
  const endTask = tasks[tasks.length - 1];
  return (
    <>
      <Head>
        <title>Rank Assistant Replies</title>
        <meta name="description" content="Rank Assistant Replies." />
      </Head>
      <main className="p-6 bg-slate-100 text-gray-800">
        <div className="rounded-lg shadow-lg block bg-white p-6 mb-8">
          <h5 className="text-lg font-semibold mb-4">Instructions</h5>
          <p className="text-lg py-1">
            Given the following replies, sort them from best to worst, best being first, worst being last.
          </p>
          <Sortable items={replies} onChange={setRanking} />
        </div>

        <section className="mb-8 p-4 rounded-lg shadow-lg bg-white flex flex-row justify-items-stretch">
          <TaskInfo id={tasks[0].id} output="Submit your answer" />

          <Flex justify="center" ml="auto" gap={2}>
            <SkipButton>Skip</SkipButton>
            {endTask.task.type !== "task_done" ? (
              <SubmitButton onClick={() => submitResponse(tasks[0])} disabled={ranking.length === 0}>
                Submit
              </SubmitButton>
            ) : (
              <SubmitButton onClick={fetchNextTask}>Next Task</SubmitButton>
            )}
          </Flex>
        </section>
      </main>
    </>
  );
};

export default RankAssistantReplies;
