import { useRef, useState } from "react";
import { TaskControls } from "src/components/Survey/TaskControls";
import { CreateTask } from "src/components/Tasks/CreateTask";
import { EvaluateTask } from "src/components/Tasks/EvaluateTask";
import { LabelTask } from "src/components/Tasks/LabelTask";
import { TaskCategory, TaskInfo, TaskInfos } from "src/components/Tasks/TaskTypes";
import { UnchangedWarning } from "src/components/Tasks/UnchangedWarning";
import { post } from "src/lib/api";
import { TaskContent, TaskReplyValidity } from "src/types/Task";
import useSWRMutation from "swr/mutation";

export type TaskStatus = "NOT_SUBMITTABLE" | "DEFAULT" | "VALID" | "REVIEW" | "SUBMITTED";

export interface TaskSurveyProps<T> {
  // we need a task type
  // eslint-disable-next-line  @typescript-eslint/no-explicit-any
  task: any;
  taskType: TaskInfo;
  isEditable: boolean;
  isDisabled?: boolean;
  onReplyChanged: (content: T) => void;
  onValidityChanged: (validity: TaskReplyValidity) => void;
}

export const Task = ({ frontendId, task, trigger, mutate }) => {
  const [taskStatus, setTaskStatus] = useState<TaskStatus>("NOT_SUBMITTABLE");
  const replyContent = useRef<TaskContent>(null);
  const [showUnchangedWarning, setShowUnchangedWarning] = useState(false);

  const rootEl = useRef<HTMLDivElement>(null);

  const taskType = TaskInfos.find((taskType) => taskType.type === task.type && taskType.mode === task.mode);

  const { trigger: sendRejection } = useSWRMutation("/api/reject_task", post, {
    onSuccess: async () => {
      mutate();
    },
  });

  const rejectTask = (reason: string) => {
    sendRejection({
      id: frontendId,
      reason,
    });
  };

  const edit_mode = taskStatus === "NOT_SUBMITTABLE" || taskStatus === "DEFAULT" || taskStatus === "VALID";
  const submitted = taskStatus === "SUBMITTED";

  const onValidityChanged = (validity: TaskReplyValidity) => {
    if (!edit_mode) return;
    switch (validity) {
      case "DEFAULT":
        if (taskStatus !== "DEFAULT") setTaskStatus("DEFAULT");
        break;
      case "VALID":
        if (taskStatus !== "VALID") setTaskStatus("VALID");
        break;
      case "INVALID":
        if (taskStatus !== "NOT_SUBMITTABLE") setTaskStatus("NOT_SUBMITTABLE");
        break;
    }
  };

  const onReplyChanged = (content: TaskContent) => {
    replyContent.current = content;
  };

  const reviewResponse = () => {
    switch (taskStatus) {
      case "DEFAULT":
        setShowUnchangedWarning(true);
        break;
      case "VALID":
        setTaskStatus("REVIEW");
        break;
      default:
        return;
    }
  };

  const editResponse = () => {
    switch (taskStatus) {
      case "REVIEW":
        setTaskStatus("VALID");
        break;
      default:
        return;
    }
  };

  const submitResponse = () => {
    switch (taskStatus) {
      case "REVIEW": {
        trigger({
          id: frontendId,
          update_type: taskType.update_type,
          content: replyContent.current,
        });
        setTaskStatus("SUBMITTED");
        scrollToTop(rootEl.current);
        break;
      }
      default:
        return;
    }
  };

  function taskTypeComponent() {
    switch (taskType.category) {
      case TaskCategory.Create:
        return (
          <CreateTask
            key={task.id}
            task={task}
            taskType={taskType}
            isEditable={edit_mode}
            isDisabled={submitted}
            onReplyChanged={onReplyChanged}
            onValidityChanged={onValidityChanged}
          />
        );
      case TaskCategory.Evaluate:
        return (
          <EvaluateTask
            key={task.id}
            task={task}
            taskType={taskType}
            isEditable={edit_mode}
            isDisabled={submitted}
            onReplyChanged={onReplyChanged}
            onValidityChanged={onValidityChanged}
          />
        );
      case TaskCategory.Label:
        return (
          <LabelTask
            key={task.id}
            task={task}
            taskType={taskType}
            isEditable={edit_mode}
            isDisabled={submitted}
            onReplyChanged={onReplyChanged}
            onValidityChanged={onValidityChanged}
          />
        );
    }
  }

  return (
    <div ref={rootEl}>
      {taskTypeComponent()}
      <TaskControls
        task={task}
        taskStatus={taskStatus}
        onEdit={editResponse}
        onReview={reviewResponse}
        onSubmit={submitResponse}
        onSkip={rejectTask}
      />
      <UnchangedWarning
        show={showUnchangedWarning}
        title={taskType.unchanged_title || "No changes"}
        message={taskType.unchanged_message || "Are you sure you would like to continue?"}
        continueButtonText={"Continue anyway"}
        onClose={() => setShowUnchangedWarning(false)}
        onContinueAnyway={() => {
          if (taskStatus === "DEFAULT") {
            setTaskStatus("REVIEW");
            setShowUnchangedWarning(false);
          }
        }}
      />
    </div>
  );
};

const scrollToTop = (element: HTMLElement) => {
  while (element) {
    element.scrollTop = 0;
    element = element.parentElement;
  }
};
