import { useState } from "react";
import { Messages } from "src/components/Messages";
import { TaskControls } from "src/components/Survey/TaskControls";
import { TrackedTextarea } from "src/components/Survey/TrackedTextarea";
import { TwoColumnsWithCards } from "src/components/Survey/TwoColumnsWithCards";
import { TaskInfo } from "src/components/Tasks/TaskTypes";

export interface CreateTaskProps {
  // we need a task type
  // eslint-disable-next-line  @typescript-eslint/no-explicit-any
  tasks: any[];
  taskType: TaskInfo;
  trigger: (update: { id: string; update_type: string; content: { text: string } }) => void;
  onSkipTask: (task: { id: string }, reason: string) => void;
  onNextTask: () => void;
  mainBgClasses: string;
}
export const CreateTask = ({ tasks, taskType, trigger, onSkipTask, onNextTask, mainBgClasses }: CreateTaskProps) => {
  const task = tasks[0].task;
  const valid_labels = tasks[0].valid_labels;
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

  const textChangeHandler = (event: React.ChangeEvent<HTMLTextAreaElement>) => {
    setInputText(event.target.value);
  };

  return (
    <div className={`p-12 ${mainBgClasses}`}>
      <TwoColumnsWithCards>
        <>
          <h5 className="text-lg font-semibold">{taskType.label}</h5>
          <p className="text-lg py-1">{taskType.overview}</p>
          {task.conversation ? (
            <Messages messages={task.conversation.messages} post_id={task.id} valid_labels={valid_labels} />
          ) : null}
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

      <TaskControls
        tasks={tasks}
        onSubmitResponse={submitResponse}
        onSkipTask={(task, reason) => {
          setInputText("");
          onSkipTask(task, reason);
        }}
        onNextTask={() => {
          onNextTask();
          setInputText("");
        }}
      />
    </div>
  );
};
