import { ArrowDownIcon, ArrowUpIcon } from "@heroicons/react/20/solid";
import clsx from "clsx";
import Head from "next/head";
import { useState } from "react";
import useSWRImmutable from "swr/immutable";
import useSWRMutation from "swr/mutation";

import fetcher from "src/lib/fetcher";
import poster from "src/lib/poster";

import { Button } from "src/components/Button";
import { LoadingScreen } from "@/components/Loading/LoadingScreen";

const RankInitialPrompts = () => {
  const [tasks, setTasks] = useState([]);
  /**
   * This array will contain the ranked indices of the prompts
   * The best prompt will have index 0, and the worst is the last.
   */
  const [ranking, setRanking] = useState<number[]>([]);

  const { isLoading } = useSWRImmutable("/api/new_task/rank_initial_prompts", fetcher, {
    onSuccess: (data) => {
      setTasks([data]);

      const indices = Array.from({ length: data.task.prompts.length }).map((_, i) => i);
      setRanking(indices);
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

  if (isLoading) {
    return <LoadingScreen text="Loading..." />;
  }

  if (tasks.length == 0) {
    return <div className="p-6 bg-slate-100 text-gray-800">No tasks found...</div>;
  }

  const prompts = tasks[0].task.prompts as string[];
  const items = ranking.map((i) => ({
    text: prompts[i],
    originalIndex: i,
  }));

  return (
    <>
      <Head>
        <title>Rank Initial Prompts</title>
        <meta name="description" content="Rank initial prompts." />
      </Head>
      <main className="p-6 bg-slate-100 text-gray-800">
        <div className="rounded-lg shadow-lg block bg-white p-6 mb-8">
          <h5 className="text-lg font-semibold mb-4">Instructions</h5>
          <p className="text-lg py-1">
            Given the following prompts, sort them from best to worst, best being first, worst being last.
          </p>
          <ul className="flex flex-col gap-4">
            {items.map(({ text, originalIndex }, i) => (
              <SortableItem
                key={`${originalIndex}_${i}`}
                canIncrement={i > 0}
                onIncrement={() => {
                  const newRanking = ranking.slice();
                  const newIdx = i - 1;
                  [newRanking[i], newRanking[newIdx]] = [newRanking[newIdx], newRanking[i]];
                  setRanking(newRanking);
                }}
                canDecrement={i < items.length - 1}
                onDecrement={() => {
                  const newRanking = ranking.slice();
                  const newIdx = i + 1;
                  [newRanking[i], newRanking[newIdx]] = [newRanking[newIdx], newRanking[i]];
                  setRanking(newRanking);
                }}
              >
                {text}
              </SortableItem>
            ))}
          </ul>
        </div>

        <section className="mb-8 p-4 rounded-lg shadow-lg bg-white flex flex-row justify-items-stretch ">
          <div className="grid grid-cols-[min-content_auto] gap-x-2 text-gray-700">
            <b>Prompt</b>
            <span>{tasks[0].id}</span>
            <b>Output</b>
            <span>Submit your answer</span>
          </div>

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

export default RankInitialPrompts;

const SortableItem = ({ canIncrement, canDecrement, onIncrement, onDecrement, children, ...props }) => {
  return (
    <li className="grid grid-cols-[min-content_1fr] items-center rounded-lg shadow-md gap-x-2 p-2">
      <ArrowButton active={canIncrement} onClick={onIncrement}>
        <ArrowUpIcon width={28} />
      </ArrowButton>
      <span style={{ gridRow: "span 2" }}>{children}</span>

      <ArrowButton active={canDecrement} onClick={onDecrement}>
        <ArrowDownIcon width={28} />
      </ArrowButton>
    </li>
  );
};

const ArrowButton = ({ children, active, onClick }) => {
  return (
    <Button
      className={clsx("justify-center", active ? "hover:bg-indigo-200" : "opacity-10")}
      onClick={onClick}
      disabled={!active}
    >
      {children}
    </Button>
  );
};
