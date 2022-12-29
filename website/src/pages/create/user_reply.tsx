import { Textarea } from "@chakra-ui/react";
import { useRef, useState } from "react";
import useSWRMutation from "swr/mutation";
import useSWRImmutable from "swr/immutable";

import fetcher from "src/lib/fetcher";
import poster from "src/lib/poster";

import { Button } from "src/components/Button";
import { LoadingScreen } from "src/components/Loading/LoadingScreen";
import { Messages } from "src/components/Messages";
import { TaskInfo } from "src/components/TaskInfo/TaskInfo";
import { TwoColumns } from "src/components/TwoColumns";

const UserReply = () => {
  const [tasks, setTasks] = useState([]);

  const inputRef = useRef<HTMLTextAreaElement>(null);

  const { isLoading } = useSWRImmutable("/api/new_task/user_reply", fetcher, {
    onSuccess: (data) => {
      console.log(data);
      setTasks([data]);
    },
  });

  const { trigger, isMutating } = useSWRMutation("/api/update_task", poster, {
    onSuccess: async (data) => {
      const newTask = await data.json();
      setTasks((oldTasks) => [...oldTasks, newTask]);
    },
  });

  const submitResponse = (task: { id: string }) => {
    const text = inputRef.current.value.trim();
    trigger({
      id: task.id,
      update_type: "text_reply_to_post",
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

  const task = tasks[0].task;
  return (
    <div className="p-6 bg-slate-100 text-gray-800">
      <TwoColumns>
        <>
          <h5 className="text-lg font-semibold">Reply as a user</h5>
          <p className="text-lg py-1">Given the following conversation, provide an adequate reply</p>
          <Messages messages={task.conversation.messages} />
          {task.hint && <p className="text-lg py-1">Hint: {task.hint}</p>}
        </>
        <Textarea name="reply" placeholder="Reply..." ref={inputRef} />
      </TwoColumns>

      <section className="mb-8 p-4 rounded-lg shadow-lg bg-white flex flex-row justify-items-stretch ">
        <TaskInfo id={tasks[0].id} output="Submit your answer" />

        <div className="flex justify-center ml-auto">
          <Button className="mr-2 bg-indigo-100 text-indigo-700 hover:bg-indigo-200">Skip</Button>
          <Button
            onClick={() => submitResponse(tasks[0])}
            className="bg-indigo-600 text-white shadow-sm hover:bg-indigo-700"
          >
            Submit
          </Button>
        </div>
      </section>
    </div>
  );
};

export default UserReply;
