import { useState } from "react";
import { LoadingScreen } from "src/components/Loading/LoadingScreen";
import { MessageView } from "src/components/Messages";
import { TaskControls } from "src/components/Survey/TaskControls";
import { LabelSliderGroup, LabelTask } from "src/components/Tasks/LabelTask";
import {
  LabelInitialPromptTaskResponse,
  useLabelInitialPromptTask,
} from "src/hooks/tasks/labeling/useLabelInitialPrompt";

const LabelInitialPrompt = () => {
  const [sliderValues, setSliderValues] = useState<number[]>([]);

  const { tasks, isLoading, submit, reset } = useLabelInitialPromptTask();

  if (isLoading || tasks.length === 0) {
    return <LoadingScreen />;
  }

  const task = tasks[0].task;

  return (
    <LabelTask
      title="Label Initial Prompt"
      desc="Provide labels for the following prompt"
      messages={<MessageView text={task.prompt} is_assistant message_id={task.message_id} />}
      inputs={<LabelSliderGroup labelIDs={task.valid_labels} onChange={setSliderValues} />}
      controls={
        <TaskControls
          tasks={tasks}
          onSkipTask={() => reset()}
          onNextTask={reset}
          onSubmitResponse={({ id, task }: LabelInitialPromptTaskResponse) =>
            submit(id, task.message_id, task.prompt, task.valid_labels, sliderValues)
          }
        />
      }
    />
  );
};

export default LabelInitialPrompt;
