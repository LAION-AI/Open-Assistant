import { useTranslation } from "next-i18next";
import { useCallback, useEffect, useReducer } from "react";
import { useMemo, useRef } from "react";
import { TaskControls } from "src/components/Survey/TaskControls";
import { CreateTask } from "src/components/Tasks/CreateTask";
import { EvaluateTask } from "src/components/Tasks/EvaluateTask";
import { LabelTask } from "src/components/Tasks/LabelTask";
import { UnchangedWarning } from "src/components/Tasks/UnchangedWarning";
import { useTaskContext } from "src/context/TaskContext";
import { getTypeSafei18nKey } from "src/lib/i18n";
import { TaskCategory, TaskInfo } from "src/types/Task";
import { BaseTask, TaskContent, TaskReplyValidity } from "src/types/Task";
import { CreateTaskType, LabelTaskType, RankTaskType } from "src/types/Tasks";

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

export interface TaskSurveyProps<TaskType extends BaseTask, ReplyContent> {
  task: TaskType;
  taskType: TaskInfo;
  isEditable: boolean;
  isDisabled?: boolean;
  onReplyChanged: (content: ReplyContent) => void;
  onValidityChanged: (validity: TaskReplyValidity) => void;
}

export const Task = () => {
  const { t } = useTranslation("tasks");
  const rootEl = useRef<HTMLDivElement>(null);
  const replyContent = useRef<TaskContent>(null);
  const { rejectTask, completeTask, isLoading, task, taskInfo } = useTaskContext();
  const [taskStatus, taskEvent] = useReducer(
    (
      status: TaskStatus,
      event: NewTask | UpdateValidity | AcceptDefault | Review | ReturnToEdit | SetSubmitted
    ): TaskStatus => {
      switch (event.action) {
        case "NEW_TASK":
          return status.mode !== "EDIT" ? { mode: "EDIT", replyValidity: "INVALID" } : status;
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

  const updateValidity = useCallback(
    (replyValidity: TaskReplyValidity) => taskEvent({ action: "UPDATE_VALIDITY", replyValidity }),
    [taskEvent]
  );

  useEffect(() => {
    taskEvent({ action: "NEW_TASK" });
    scrollToTop(rootEl.current);
  }, [task.id]);

  const onReplyChanged = useCallback(
    (content: TaskContent) => {
      replyContent.current = content;
    },
    [replyContent]
  );

  const submitResponse = useCallback(async () => {
    if (taskStatus.mode === "REVIEW") {
      taskEvent({ action: "SET_SUBMITTED" });
      await completeTask(replyContent.current);
    }
  }, [taskStatus.mode, completeTask]);

  const taskTypeComponent = useMemo(() => {
    switch (taskInfo.category) {
      case TaskCategory.Create:
        return (
          <CreateTask
            task={task as CreateTaskType}
            taskType={taskInfo}
            isEditable={taskStatus.mode === "EDIT"}
            isDisabled={taskStatus.mode === "SUBMITTED"}
            onReplyChanged={onReplyChanged}
            onValidityChanged={updateValidity}
          />
        );
      case TaskCategory.Evaluate:
        return (
          <EvaluateTask
            task={task as RankTaskType}
            taskType={taskInfo}
            isEditable={taskStatus.mode === "EDIT"}
            isDisabled={taskStatus.mode === "SUBMITTED"}
            onReplyChanged={onReplyChanged}
            onValidityChanged={updateValidity}
          />
        );
      case TaskCategory.Label:
        return (
          <LabelTask
            task={task as LabelTaskType}
            taskType={taskInfo}
            isEditable={taskStatus.mode === "EDIT"}
            isDisabled={taskStatus.mode === "SUBMITTED"}
            onReplyChanged={onReplyChanged}
            onValidityChanged={updateValidity}
          />
        );
    }
  }, [taskInfo, task, taskStatus.mode, onReplyChanged, updateValidity]);

  return (
    <div ref={rootEl}>
      {taskTypeComponent}
      <TaskControls
        task={task}
        taskStatus={taskStatus}
        isLoading={isLoading}
        onEdit={() => taskEvent({ action: "RETURN_EDIT" })}
        onReview={() => taskEvent({ action: "REVIEW" })}
        onSubmit={submitResponse}
        onSkip={rejectTask}
      />
      <UnchangedWarning
        show={taskStatus.mode === "DEFAULT_WARN"}
        title={t(getTypeSafei18nKey(`${taskInfo.id}.unchanged_title`), t("default.unchanged_title"))}
        message={t(getTypeSafei18nKey(`${taskInfo.id}.unchanged_message`), t("default.unchanged_message"))}
        continueButtonText={t(getTypeSafei18nKey(`${taskInfo.id}.continue_anyway`), t("default.continue_anyway"))}
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
