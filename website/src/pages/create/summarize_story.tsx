import { Flex, Textarea } from "@chakra-ui/react";
import Head from "next/head";
import { useRef, useState } from "react";
import { SkipButton } from "src/components/Buttons/Skip";
import { SubmitButton } from "src/components/Buttons/Submit";
import { LoadingScreen } from "src/components/Loading/LoadingScreen";
import { TaskInfo } from "src/components/TaskInfo/TaskInfo";
import { TwoColumns } from "src/components/TwoColumns";
import fetcher from "src/lib/fetcher";
import poster from "src/lib/poster";
import useSWRImmutable from "swr/immutable";
import useSWRMutation from "swr/mutation";

const SummarizeStory = () => {
  // Use an array of tasks that record the sequence of steps until a task is
  // deemed complete.
  const [tasks, setTasks] = useState([]);

  const inputRef = useRef<HTMLTextAreaElement>(null);

  // Fetch the very fist task.  We can ignore everything except isLoading
  // because the onSuccess handler will update `tasks` when ready.
  const { isLoading } = useSWRImmutable("/api/new_task/summarize_story", fetcher, {
    onSuccess: (data) => {
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
      update_type: "text_reply_to_message",
      content: {
        text,
      },
    });
  };

  if (isLoading) {
    return <LoadingScreen text="Loading..." />;
  }

  if (tasks.length == 0) {
    return <div className="p-6 bg-slate-100 text-gray-800">No tasks found...</div>;
  }

  return (
    <>
      <Head>
        <title>Summarize A Story</title>
        <meta name="description" content="Summarize a story to train our model." />
      </Head>
      <main className="p-6 h-full mx-auto bg-slate-100 text-gray-800">
        <TwoColumns>
          <>
            <h5 className="text-lg font-semibold">Instruction</h5>
            <p className="text-lg py-1">Summarize the following story</p>
            <div className="bg-slate-800 p-6 rounded-xl text-white whitespace-pre-wrap">{tasks[0].task.story}</div>
          </>
          <Textarea name="summary" placeholder="Summary" ref={inputRef} />
        </TwoColumns>

        <section className="mb-8 p-4 rounded-lg shadow-lg bg-white flex flex-row justify-items-stretch ">
          <TaskInfo id={tasks[0].id} output="Submit your answer" />

          <Flex justify="center" ml="auto" gap={2}>
            <SkipButton>Skip</SkipButton>
            <SubmitButton onClick={() => submitResponse(tasks[0])}>Submit</SubmitButton>
          </Flex>
        </section>
      </main>
    </>
  );
};

export default SummarizeStory;
