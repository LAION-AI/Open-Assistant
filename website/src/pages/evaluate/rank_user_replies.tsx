import Head from "next/head";
import { useState } from "react";
import useSWRImmutable from "swr/immutable";
import useSWRMutation from "swr/mutation";

import fetcher from "src/lib/fetcher";
import poster from "src/lib/poster";

import { Button } from "src/components/Button";
import { Sortable } from "src/components/Sortable/Sortable";
import { TaskInfo } from "src/components/TaskInfo/TaskInfo";

const RankUserReplies = () => {
  const [tasks, setTasks] = useState([]);
  /**
   * This array will contain the ranked indices of the replies
   * The best reply will have index 0, and the worst is the last.
   */
  const [ranking, setRanking] = useState<number[]>([]);

  const { isLoading } = useSWRImmutable("/api/new_task/rank_user_replies", fetcher, {
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
      update_type: "post_ranking",
      content: {
        ranking,
      },
    });
  };

  /**
   * TODO: Make this a nicer loading screen.
   */
  if (tasks.length == 0) {
    return <div className="p-6 bg-slate-100 text-gray-800">Loading...</div>;
  }
  const replies = tasks[0].task.replies as string[];

  return (
    <>
      <Head>
        <title>Rank User Replies</title>
        <meta name="description" content="Rank User Replies." />
      </Head>
      <main className="p-6 bg-slate-100 text-gray-800">
        <div className="rounded-lg shadow-lg block bg-white p-6 mb-8">
          <h5 className="text-lg font-semibold mb-4">Instructions</h5>
          <p className="text-lg py-1">
            Given the following replies, sort them from best to worst, best being first, worst being last.
          </p>
          <Sortable items={replies} onChange={setRanking} />
        </div>

        <section className="mb-8 p-4 rounded-lg shadow-lg bg-white flex flex-row justify-items-stretch ">
          <TaskInfo id={tasks[0].id} output="Submit your answer" />

          <div className="flex justify-center ml-auto">
            <Button className="mr-2 bg-indigo-100 text-indigo-700 hover:bg-indigo-200">Skip</Button>
            <Button
              onClick={() => submitResponse(tasks[0])}
              disabled={ranking.length === 0}
              className="bg-indigo-600 text-white shadow-sm hover:bg-indigo-700"
            >
              Submit
            </Button>
          </div>
        </section>
      </main>
    </>
  );
};

export default RankUserReplies;
