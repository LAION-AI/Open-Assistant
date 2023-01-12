import { useState } from "react";
import { Messages } from "src/components/Messages";
import { TrackedTextarea } from "src/components/Survey/TrackedTextarea";
import { TwoColumnsWithCards } from "src/components/Survey/TwoColumnsWithCards";
import { TaskSurveyProps } from "src/components/Tasks/Task";

export const CreateTask = ({ task, taskType, onReplyChanged }: TaskSurveyProps<{ text: string }>) => {
  const [inputText, setInputText] = useState("");

  const textChangeHandler = (event: React.ChangeEvent<HTMLTextAreaElement>) => {
    const text = event.target.value;
    onReplyChanged({ content: { text }, state: "VALID" });
    setInputText(text);
  };

  return (
    <div data-cy="task" data-task-type="create-task">
      <TwoColumnsWithCards>
        <>
          <h5 className="text-lg font-semibold">{taskType.label}</h5>
          <p className="text-lg py-1">{taskType.overview}</p>
          {task.conversation ? <Messages messages={task.conversation.messages} post_id={task.id} /> : null}
        </>
        <>
          <h5 className="text-lg font-semibold">{taskType.instruction}</h5>
          <TrackedTextarea
            text={inputText}
            onTextChange={textChangeHandler}
            thresholds={{ low: 20, medium: 40, goal: 50 }}
            textareaProps={{ placeholder: "Reply..." }}
          />
        </>
      </TwoColumnsWithCards>
    </div>
  );
};
