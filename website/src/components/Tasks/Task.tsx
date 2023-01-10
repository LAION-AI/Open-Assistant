import { useColorMode } from "@chakra-ui/react";
import { useRef, useState } from "react";
import { TaskControls } from "src/components/Survey/TaskControls";
import { CreateTask } from "src/components/Tasks/CreateTask";
import { EvaluateTask } from "src/components/Tasks/EvaluateTask";
import { LabelTask } from "src/components/Tasks/LabelTask";
import { TaskCategory, TaskInfo, TaskTypes } from "src/components/Tasks/TaskTypes";
import { UnchangedWarning } from "src/components/Tasks/UnchangedWarning";
import poster from "src/lib/poster";
import { TaskContent } from "src/types/Task";
import { TaskReplyState } from "src/types/TaskReplyState";
import useSWRMutation from "swr/mutation";

export type TaskStatus = "NOT_SUBMITTABLE" | "DEFAULT" | "SUBMITABLE" | "SUBMITTED";

export interface TaskSurveyProps<T> {
  // we need a task type
  // eslint-disable-next-line  @typescript-eslint/no-explicit-any
  task: any;
  taskType: TaskInfo;
  onReplyChanged: (state: TaskReplyState<T>) => void;
}

export const Task = ({ task, trigger, mutate }) => {
  const [taskStatus, setTaskStatus] = useState<TaskStatus>("NOT_SUBMITTABLE");
  const replyContent = useRef<TaskContent>(null);
  const [showUnchangedWarning, setShowUnchangedWarning] = useState(false);

  const taskType = TaskTypes.find((taskType) => taskType.type === task.type);

  const { colorMode } = useColorMode();
  const mainBgClasses = colorMode === "light" ? "bg-slate-300 text-gray-800" : "bg-slate-900 text-white";

  const { trigger: sendRejection } = useSWRMutation("/api/reject_task", poster, {
    onSuccess: async () => {
      mutate();
    },
  });

  const rejectTask = (reason: string) => {
    sendRejection({
      id: task.id,
      reason,
    });
  };

  const onReplyChanged = useRef((state: TaskReplyState<TaskContent>) => {
    if (taskStatus === "SUBMITTED") return;

    replyContent.current = state?.content;
    if (state === null) {
      if (taskStatus !== "NOT_SUBMITTABLE") setTaskStatus("NOT_SUBMITTABLE");
    } else if (state.state === "DEFAULT") {
      if (taskStatus !== "DEFAULT") setTaskStatus("DEFAULT");
    } else if (state.state === "VALID") {
      if (taskStatus !== "SUBMITABLE") setTaskStatus("SUBMITABLE");
    }
  }).current;

  const submitResponse = () => {
    switch (taskStatus) {
      case "NOT_SUBMITTABLE":
        return;
      case "DEFAULT":
        setShowUnchangedWarning(true);
        break;
      case "SUBMITABLE": {
        trigger({
          id: task.id,
          update_type: taskType.update_type,
          content: replyContent.current,
        });
        setTaskStatus("SUBMITTED");
        break;
      }
      case "SUBMITTED":
        return;
    }
  };

  function taskTypeComponent() {
    switch (taskType.category) {
      case TaskCategory.Create:
        return <CreateTask key={task.id} task={task} taskType={taskType} onReplyChanged={onReplyChanged} />;
      case TaskCategory.Evaluate:
        return <EvaluateTask key={task.id} task={task} taskType={taskType} onReplyChanged={onReplyChanged} />;
      case TaskCategory.Label:
        return <LabelTask key={task.id} task={task} taskType={taskType} onReplyChanged={onReplyChanged} />;
    }
  }

  return (
    <div className={`p-12 ${mainBgClasses}`}>
      {taskTypeComponent()}
      <TaskControls
        task={task}
        taskStatus={taskStatus}
        onSubmit={submitResponse}
        onSkip={rejectTask}
        onNextTask={mutate}
      />
      <UnchangedWarning
        show={showUnchangedWarning}
        title={taskType.unchanged_title || "No changes"}
        message={taskType.unchanged_message || "Are you sure you would like to submit?"}
        onClose={() => setShowUnchangedWarning(false)}
        onSubmitAnyway={() => {
          if (taskStatus === "DEFAULT") {
            trigger({
              id: task.id,
              update_type: taskType.update_type,
              content: replyContent.current,
            });
            setTaskStatus("SUBMITTED");
            setShowUnchangedWarning(false);
          }
        }}
      />
    </div>
  );
};
