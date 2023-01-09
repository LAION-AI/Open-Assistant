import { useState } from "react";
import { LoadingScreen } from "src/components/Loading/LoadingScreen";
import { Message } from "src/components/Messages";
import { MessageTable } from "src/components/Messages/MessageTable";
import { TaskControls } from "src/components/Survey/TaskControls";
import { LabelSliderGroup, LabelTask } from "src/components/Tasks/LabelTask";
import {
  LabelAssistantReplyTaskResponse,
  useLabelAssistantReplyTask,
} from "src/hooks/tasks/labeling/useLabelAssistantReply";

const LabelAssistantReply = () => {
  const [sliderValues, setSliderValues] = useState<number[]>([]);

  const { tasks, isLoading, submit, reset } = useLabelAssistantReplyTask();

  if (isLoading || tasks.length === 0) {
    return <LoadingScreen />;
  }

  const task = tasks[0].task;
  const messages: Message[] = [
    ...task.conversation.messages,
    { text: task.reply, is_assistant: true, message_id: task.message_id },
  ];

  return (
    <LabelTask
      title="Label Assistant Reply"
      desc="Given the following discussion, provide labels for the final prompt"
      messages={<MessageTable messages={messages} />}
      inputs={<LabelSliderGroup labelIDs={task.valid_labels} onChange={setSliderValues} />}
      controls={
        <TaskControls
          tasks={tasks}
          onSkipTask={() => reset()}
          onNextTask={reset}
          onSubmitResponse={({ id, task }: LabelAssistantReplyTaskResponse) =>
            submit(id, task.message_id, task.reply, task.valid_labels, sliderValues)
          }
        />
      }
    />
  );
};

export default LabelAssistantReply;
