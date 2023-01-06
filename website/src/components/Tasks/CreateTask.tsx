import { Textarea } from "@chakra-ui/react";
import { useRef } from "react";
import { Messages } from "src/components/Messages";
import { TaskControls } from "src/components/Survey/TaskControls";
import { TwoColumnsWithCards } from "src/components/Survey/TwoColumnsWithCards";

const CreateTask = ({ tasks, taskType, trigger, mutate, mainBgClasses }) => {
  const inputRef = useRef<HTMLTextAreaElement>(null);

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

  const task = tasks[0].task;

  return (
    <div className={`p-12 ${mainBgClasses}`}>
      <TwoColumnsWithCards>
        <>
          <h5 className="text-lg font-semibold">{taskType.header}</h5>
          <p className="text-lg py-1">{taskType.instructions}</p>
          {task.conversation != null ? <Messages messages={task.conversation.messages} post_id={task.id} /> : null}
        </>
        <Textarea name="reply" data-cy="reply" placeholder="Reply..." ref={inputRef} />
      </TwoColumnsWithCards>

      <TaskControls tasks={tasks} onSubmitResponse={submitResponse} onSkip={fetchNextTask} />
    </div>
  );
};

export default CreateTask;
