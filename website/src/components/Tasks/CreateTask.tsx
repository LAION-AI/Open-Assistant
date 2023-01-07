import { useState } from "react";
import { Messages } from "src/components/Messages";
import { TaskControls } from "src/components/Survey/TaskControls";
import { TrackedTextarea } from "src/components/Survey/TrackedTextarea";
import { TwoColumnsWithCards } from "src/components/Survey/TwoColumnsWithCards";

export const CreateTask = ({ tasks, trigger, mutate, mainBgClasses }) => {
  const task = tasks[0].task;

  const [inputText, setInputText] = useState("");

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

  return (
    <div className={`p-12 ${mainBgClasses}`}>
      <TwoColumnsWithCards>
        <>
          <h5 className="text-lg font-semibold">Reply as the assistant</h5>
          <p className="text-lg py-1">Given the following conversation, provide an adequate reply</p>
          {task.conversation ? <Messages messages={task.conversation.messages} post_id={task.id} /> : null}
        </>
        <>
          <h5 className="text-lg font-semibold">Provide the assistant`s reply</h5>
          <TrackedTextarea
            text={inputText}
            onTextChange={textChangeHandler}
            thresholds={{ low: 20, medium: 40, goal: 50 }}
            textareaProps={{ placeholder: "Reply..." }}
          />
        </>
      </TwoColumnsWithCards>

      <TaskControls tasks={tasks} onSubmitResponse={submitResponse} onSkip={fetchNextTask} />
    </div>
  );
};
