// TODO(#65): Unify and simplify the task paths
import { Textarea } from "@chakra-ui/react";
import { useRef, useState } from "react";
import useSWRMutation from "swr/mutation";
import useSWRImmutable from "swr/immutable";

import fetcher from "src/lib/fetcher";
import poster from "src/lib/poster";

const SummarizeStory = () => {
  // Use an array of tasks that record the sequence of steps until a task is
  // deemed complete.
  const [tasks, setTasks] = useState([]);

  const inputRef = useRef<HTMLTextAreaElement>(null);

  // Fetch the very fist task.  We can ignore everything except isLoading
  // because the onSuccess handler will update `tasks` when ready.
  const { isLoading } = useSWRImmutable("/api/new_task/summarize_story", fetcher, {
    onSuccess: (data) => {
      console.log(data);
      setTasks([data]);
    },
  });

  // Every time we submit an answer to the latest task, let the backend handle
  // all the interactions then add the resulting task to the queue.  This ends
  // when we hit the done task.
  const { trigger, isMutating } = useSWRMutation("/api/update_task", poster, {
    onSuccess: async (data) => {
      const newTask = await data.json();
      // This is the more efficient way to update a react state array.
      setTasks((oldTasks) => [...oldTasks, newTask]);
    },
  });

  // Trigger a mutation that updates the current task.  We should probably
  // signal somewhere that this interaction is being processed.
  const submitResponse = (task: { id: string }) => {
    const text = inputRef.current.value.trim();
    trigger({
      id: task.id,
      content: {
        update_type: "text_reply_to_post",
        text,
      },
    });
  };

  /**
   * TODO: Make this a nicer loading screen.
   */
  if (tasks.length == 0) {
    return <div className=" p-6 h-full mx-auto bg-slate-100 text-gray-800">Loading...</div>;
  }

  return (
    <div className=" p-6 h-full mx-auto bg-slate-100 text-gray-800">
      {/* Instrunction and Output panels */}
      <section className="mb-8  lt-lg:mb-12 ">
        <div className="grid lg:gap-x-12 lg:grid-cols-2">
          {/* Instruction panel */}
          <div className="rounded-lg shadow-lg h-full block bg-white">
            <div className="p-6">
              <h5 className="text-lg font-semibold">Instruction</h5>
              <p className="text-lg py-1">Summarize the following story</p>
              <div className="bg-slate-800 p-6 rounded-xl text-white whitespace-pre-wrap">{tasks[0].task.story}</div>
            </div>
          </div>

          {/* Output panel */}
          <div className="mt-6 lg:mt-0 rounded-lg shadow-lg h-full block bg-white">
            <div className="flex justify-center p-6">
              <Textarea name="summary" placeholder="Summary" ref={inputRef} />
            </div>
          </div>
        </div>
      </section>

      {/* Info & controls */}
      <section className="mb-8 p-4 rounded-lg shadow-lg bg-white flex flex-row justify-items-stretch ">
        <div className="flex flex-col justify-self-start text-gray-700">
          <div>
            <span>
              <b>Prompt</b>
            </span>
            <span className="ml-2">{tasks[0].id}</span>
          </div>
          <div>
            <span>
              <b>Output</b>
            </span>
            <span className="ml-2">Submit your answer</span>
          </div>
        </div>

        {/* Skip / Submit controls */}
        <div className="flex justify-center ml-auto">
          <button
            type="button"
            className="mr-2 inline-flex items-center rounded-md border border-transparent bg-indigo-100 px-4 py-2 text-sm font-medium text-indigo-700 hover:bg-indigo-200 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2"
          >
            Skip
          </button>
          <button
            type="button"
            onClick={() => submitResponse(tasks[0])}
            className="inline-flex items-center rounded-md border border-transparent bg-indigo-600 px-4 py-2 text-sm font-medium text-white shadow-sm hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2"
          >
            Submit
          </button>
        </div>
      </section>
    </div>
  );
};

export default SummarizeStory;
