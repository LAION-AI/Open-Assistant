import { useTranslation } from "next-i18next";
import { useCallback, useEffect, useReducer } from "react";
import { useMemo, useRef } from "react";
import { TaskControls } from "src/components/Survey/TaskControls";
import { CreateTask } from "src/components/Tasks/CreateTask";
import { EvaluateTask } from "src/components/Tasks/EvaluateTask";
import { LabelTask } from "src/components/Tasks/LabelTask";
import { TaskCategory, TaskInfo, TaskInfos } from "src/components/Tasks/TaskTypes";
import { UnchangedWarning } from "src/components/Tasks/UnchangedWarning";
import { post } from "src/lib/api";
import { getTypeSafei18nKey } from "src/lib/i18n";
import { BaseTask, TaskContent, TaskReplyValidity } from "src/types/Task";
import useSWRMutation from "swr/mutation";

interface EditMode {
  mode: "EDIT";
  replyValidity: TaskReplyValidity;
}
interface ReviewMode {
  mode: "REVIEW";
}
interface DefaultWarnMode {
  mode: "DEFAULT_WARN";
}
interface SubmittedMode {
  mode: "SUBMITTED";
}

export type TaskStatus = EditMode | DefaultWarnMode | ReviewMode | SubmittedMode;

interface NewTask {
  action: "NEW_TASK";
}

interface Review {
  action: "REVIEW";
}

interface SetSubmitted {
  action: "SET_SUBMITTED";
}

interface ReturnToEdit {
  action: "RETURN_EDIT";
}

interface AcceptDefault {
  action: "ACCEPT_DEFAULT";
}

interface UpdateValidity {
  action: "UPDATE_VALIDITY";
  replyValidity: TaskReplyValidity;
}

export interface TaskSurveyProps<TaskType extends BaseTask, T> {
  task: TaskType;
  taskType: TaskInfo;
  isEditable: boolean;
  isDisabled?: boolean;
  onReplyChanged: (content: T) => void;
  onValidityChanged: (validity: TaskReplyValidity) => void;
}

export const Task = ({ frontendId, task, trigger, mutate }) => {
  const { t } = useTranslation("tasks");
  const [taskStatus, taskEvent] = useReducer(
    (
      status: TaskStatus,
      event: NewTask | UpdateValidity | AcceptDefault | Review | ReturnToEdit | SetSubmitted
    ): TaskStatus => {
      switch (event.action) {
        case "NEW_TASK":
          return { mode: "EDIT", replyValidity: "INVALID" };
        case "UPDATE_VALIDITY":
          return status.mode === "EDIT" ? { mode: "EDIT", replyValidity: event.replyValidity } : status;
        case "ACCEPT_DEFAULT":
          return status.mode === "DEFAULT_WARN" ? { mode: "REVIEW" } : status;
        case "REVIEW": {
          if (status.mode === "EDIT") {
            switch (status.replyValidity) {
              case "DEFAULT":
                return { mode: "DEFAULT_WARN" };
              case "VALID":
                return { mode: "REVIEW" };
            }
          }
          return status;
        }
        case "RETURN_EDIT": {
          switch (status.mode) {
            case "REVIEW":
              return { mode: "EDIT", replyValidity: "VALID" };
            case "DEFAULT_WARN":
              return { mode: "EDIT", replyValidity: "DEFAULT" };
            default:
              return status;
          }
        }
        case "SET_SUBMITTED": {
          return status.mode === "REVIEW" ? { mode: "SUBMITTED" } : status;
        }
      }
    },
    { mode: "EDIT", replyValidity: "INVALID" }
  );

  const replyContent = useRef<TaskContent>(null);
  console.log("RENDER", taskStatus);
  const updateValidity = useCallback(
    (replyValidity: TaskReplyValidity) => taskEvent({ action: "UPDATE_VALIDITY", replyValidity }),
    [taskEvent]
  );

  useEffect(() => {
    taskEvent({ action: "NEW_TASK" });
  }, [task.id, updateValidity]);

  const rootEl = useRef<HTMLDivElement>(null);

  const taskType = useMemo(
    () => TaskInfos.find((taskType) => taskType.type === task.type && taskType.mode === task.mode),
    [task.type, task.mode]
  );

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

  const onReplyChanged = useCallback(
    (content: TaskContent) => {
      replyContent.current = content;
    },
    [replyContent]
  );

  const submitResponse = () => {
    if (taskStatus.mode === "REVIEW") {
      trigger({
        id: frontendId,
        update_type: taskType.update_type,
        content: replyContent.current,
      });
      taskEvent({ action: "SET_SUBMITTED" });
      scrollToTop(rootEl.current);
    }
  };

  const taskTypeComponent = useMemo(() => {
    switch (taskType.category) {
      case TaskCategory.Create:
        return (
          <CreateTask
            task={task}
            taskType={taskType}
            isEditable={taskStatus.mode === "EDIT"}
            isDisabled={taskStatus.mode === "SUBMITTED"}
            onReplyChanged={onReplyChanged}
            onValidityChanged={updateValidity}
          />
        );
      case TaskCategory.Evaluate:
        return (
          <EvaluateTask
            task={task}
            taskType={taskType}
            isEditable={taskStatus.mode === "EDIT"}
            isDisabled={taskStatus.mode === "SUBMITTED"}
            onReplyChanged={onReplyChanged}
            onValidityChanged={updateValidity}
          />
        );
      case TaskCategory.Label:
        return (
          <LabelTask
            task={task}
            taskType={taskType}
            isEditable={taskStatus.mode === "EDIT"}
            isDisabled={taskStatus.mode === "SUBMITTED"}
            onReplyChanged={onReplyChanged}
            onValidityChanged={updateValidity}
          />
        );
    }
  }, [task, taskType, taskStatus.mode, onReplyChanged, updateValidity]);

  return (
    <div ref={rootEl}>
      {taskTypeComponent}
      <TaskControls
        task={task}
        taskStatus={taskStatus}
        onEdit={() => taskEvent({ action: "RETURN_EDIT" })}
        onReview={() => taskEvent({ action: "REVIEW" })}
        onSubmit={submitResponse}
        onSkip={rejectTask}
      />
      <UnchangedWarning
        show={taskStatus.mode === "DEFAULT_WARN"}
        title={t(getTypeSafei18nKey(`${taskType.id}.unchanged_title`)) || t("default.unchanged_title")}
        message={t(getTypeSafei18nKey(`${taskType.id}.unchanged_message`)) || t("default.unchanged_message")}
        continueButtonText={"Continue anyway"}
        onClose={() => taskEvent({ action: "RETURN_EDIT" })}
        onContinueAnyway={() => {
          taskEvent({ action: "ACCEPT_DEFAULT" });
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
