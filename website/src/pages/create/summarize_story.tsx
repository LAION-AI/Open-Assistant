import { useColorMode } from "@chakra-ui/react";
import { useState } from "react";
import { LoadingScreen } from "src/components/Loading/LoadingScreen";
import { TaskControls } from "src/components/Survey/TaskControls";
import { TrackedTextarea } from "src/components/Survey/TrackedTextarea";
import { TwoColumnsWithCards } from "src/components/Survey/TwoColumnsWithCards";
import fetcher from "src/lib/fetcher";
import poster from "src/lib/poster";
import useSWRImmutable from "swr/immutable";
import useSWRMutation from "swr/mutation";

const SummarizeStory = () => {
  // Use an array of tasks that record the sequence of steps until a task is
  // deemed complete.
  const [tasks, setTasks] = useState([]);
  const [inputText, setInputText] = useState("");

  // Fetch the very fist task.  We can ignore everything except isLoading
  // because the onSuccess handler will update `tasks` when ready.
  const { isLoading, mutate } = useSWRImmutable("/api/new_task/summarize_story", fetcher, {
    onSuccess: (data) => {
      setTasks([data]);
    },
  });

  // Every time we submit an answer to the latest task, let the backend handle
  // all the interactions then add the resulting task to the queue.  This ends
  // when we hit the done task.
  const { trigger } = useSWRMutation("/api/update_task", poster, {
    onSuccess: async (data) => {
      const newTask = await data.json();
      // This is the more efficient way to update a react state array.
      setTasks((oldTasks) => [...oldTasks, newTask]);
    },
  });

  // Trigger a mutation that updates the current task.  We should probably
  // signal somewhere that this interaction is being processed.
  const submitResponse = (task: { id: string }) => {
    const text = inputText.trim();
    trigger({
      id: task.id,
      update_type: "text_reply_to_message",
      content: {
        text,
      },
    });
  };

  const fetchNextTask = () => {
    setInputText("");
    mutate();
  };

  const textChangeHandler = (event: React.ChangeEvent<HTMLTextAreaElement>) => {
    setInputText(event.target.value);
  };

  const { colorMode } = useColorMode();
  const mainBgClasses = colorMode === "light" ? "bg-slate-300 text-gray-800" : "bg-slate-900 text-white";

  if (isLoading) {
    return <LoadingScreen text="Loading..." />;
  }

  if (tasks.length == 0) {
    return <div className="p-6 bg-slate-100 text-gray-800">No tasks found...</div>;
  }

  return (
    <div className={`p-12 ${mainBgClasses}`}>
      <main className="p-6 h-full mx-auto bg-slate-100 text-gray-800">
        <TwoColumnsWithCards>
          <>
            <h5 className="text-lg font-semibold">Instruction</h5>
            <p className="text-lg py-1">Summarize the following story</p>
            <div className="bg-slate-800 p-6 rounded-xl text-white whitespace-pre-wrap">{tasks[0].task.story}</div>
          </>
          <>
            <h5 className="text-lg font-semibold">Provide the assistant`s reply</h5>
            <TrackedTextarea
              text={inputText}
              onTextChange={textChangeHandler}
              thresholds={{ low: 20, medium: 40, goal: 50 }}
              textareaProps={{ placeholder: "Summary" }}
            />
          </>
        </TwoColumnsWithCards>

        <TaskControls
          tasks={tasks}
          onSubmitResponse={submitResponse}
          onSkipTask={fetchNextTask}
          onNextTask={fetchNextTask}
        />
      </main>
    </div>
  );
};

export default SummarizeStory;
