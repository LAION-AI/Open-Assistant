import { Textarea } from "@chakra-ui/react";
import { useColorMode } from "@chakra-ui/react";
import { useRef, useState } from "react";
import { LoadingScreen } from "src/components/Loading/LoadingScreen";
import { Messages } from "src/components/Messages";
import { TaskControls } from "src/components/Survey/TaskControls";
import { TwoColumnsWithCards } from "src/components/Survey/TwoColumnsWithCards";
import fetcher from "src/lib/fetcher";
import poster from "src/lib/poster";
import useSWRImmutable from "swr/immutable";
import useSWRMutation from "swr/mutation";

const UserReply = () => {
  const [tasks, setTasks] = useState([]);

  const inputRef = useRef<HTMLTextAreaElement>(null);

  const { isLoading, mutate } = useSWRImmutable("/api/new_task/prompter_reply", fetcher, {
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

  const fetchNextTask = () => {
    inputRef.current.value = "";
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

  const task = tasks[0].task;

  return (
    <div className={`p-12 ${mainBgClasses}`}>
      <TwoColumnsWithCards>
        <>
          <h5 className="text-lg font-semibold">Reply as a user</h5>
          <p className="text-lg py-1">Given the following conversation, provide an adequate reply</p>
          <Messages messages={task.conversation.messages} post_id={task.id} />
          {task.hint && <p className="text-lg py-1">Hint: {task.hint}</p>}
        </>
        <Textarea name="reply" placeholder="Reply..." ref={inputRef} />
      </TwoColumnsWithCards>

      <TaskControls tasks={tasks} onSubmitResponse={submitResponse} onSkip={fetchNextTask} />
    </div>
  );
};

export default UserReply;
