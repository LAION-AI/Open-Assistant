import { useState } from "react";
import { LoadingScreen } from "src/components/Loading/LoadingScreen";
import { Message } from "src/components/Messages";
import { MessageTable } from "src/components/Messages/MessageTable";
import { TaskControls } from "src/components/Survey/TaskControls";
import { LabelSliderGroup, LabelTask } from "src/components/Tasks/LabelTask";
import {
  LabelPrompterReplyTaskResponse,
  useLabelPrompterReplyTask,
} from "src/hooks/tasks/labeling/useLabelPrompterReply";

const LabelPrompterReply = () => {
  const [sliderValues, setSliderValues] = useState<number[]>([]);

  const { tasks, isLoading, submit, reset } = useLabelPrompterReplyTask();

  if (isLoading || tasks.length === 0) {
    return <LoadingScreen />;
  }

  const task = tasks[0].task;
  const messages: Message[] = [
    ...task.conversation.messages,
    { text: task.reply, is_assistant: false, message_id: task.message_id },
  ];

  return (
    <LabelTask
      title="Label Prompter Reply"
      desc="Given the following discussion, provide labels for the final prompt"
      messages={<MessageTable messages={messages} />}
      inputs={<LabelSliderGroup labelIDs={task.valid_labels} onChange={setSliderValues} />}
      controls={
        <TaskControls
          tasks={tasks}
          onSkipTask={() => reset()}
          onNextTask={reset}
          onSubmitResponse={({ id, task }: LabelPrompterReplyTaskResponse) =>
            submit(id, task.message_id, task.reply, task.valid_labels, sliderValues)
          }
        />
      }
    />
  );
};

export default LabelPrompterReply;
