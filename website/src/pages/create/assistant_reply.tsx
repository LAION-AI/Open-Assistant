import { Flex, Textarea } from "@chakra-ui/react";
import { useRef, useState } from "react";
import useSWRMutation from "swr/mutation";
import useSWRImmutable from "swr/immutable";

import fetcher from "src/lib/fetcher";
import poster from "src/lib/poster";

import { Messages } from "src/components/Messages";
import { TwoColumns } from "src/components/TwoColumns";
import { LoadingScreen } from "src/components/Loading/LoadingScreen";
import { TaskInfo } from "src/components/TaskInfo/TaskInfo";
import { SkipButton } from "src/components/Buttons/Skip";
import { SubmitButton } from "src/components/Buttons/Submit";

const AssistantReply = () => {
  const [tasks, setTasks] = useState([]);

  const inputRef = useRef<HTMLTextAreaElement>(null);

  const { isLoading } = useSWRImmutable("/api/new_task/assistant_reply ", fetcher, {
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
          <h5 className="text-lg font-semibold">Reply as the assistant</h5>
          <p className="text-lg py-1">Given the following conversation, provide an adequate reply</p>
          <Messages messages={task.conversation.messages} />
        </>
        <Textarea name="reply" placeholder="Reply..." ref={inputRef} />
      </TwoColumns>

      <section className="mb-8 p-4 rounded-lg shadow-lg bg-white flex flex-row justify-items-stretch ">
        <TaskInfo id={tasks[0].id} output="Submit your answer" />

        <Flex justify="center" ml="auto" gap={2}>
          <SkipButton>Skip</SkipButton>
          <SubmitButton onClick={() => submitResponse(tasks[0])}>Submit</SubmitButton>
        </Flex>
      </section>
    </div>
  );
};

export default AssistantReply;
