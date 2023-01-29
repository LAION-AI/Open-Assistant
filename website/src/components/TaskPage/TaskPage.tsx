import Head from "next/head";
import { useTranslation } from "next-i18next";
import { TaskEmptyState } from "src/components/EmptyState";
import { LoadingScreen } from "src/components/Loading/LoadingScreen";
import { Task } from "src/components/Tasks/Task";
import { TaskInfos } from "src/components/Tasks/TaskTypes";
import { taskApiHooks } from "src/lib/constants";
import { getTypeSafei18nKey } from "src/lib/i18n";
import { TaskType } from "src/types/Task";
import { KnownTaskType } from "src/types/Tasks";

type TaskPageProps = {
  type: TaskType;
};

export const TaskPage = ({ type }: TaskPageProps) => {
  const { t } = useTranslation(["tasks", "common"]);
  const taskApiHook = taskApiHooks[type];
  const { response, isLoading, completeTask, skipTask } = taskApiHook(type);
  const taskInfo = TaskInfos.find((taskType) => taskType.type === type);

  let body;
  switch (response.taskAvailability) {
    case "AWAITING_INITIAL":
      body = <LoadingScreen text={t("common:loading")} />;
      break;
    case "NONE_AVAILABLE":
      body = <TaskEmptyState />;
      break;
    case "AVAILABLE":
      body = (
        <Task
          key={response.task.id}
          frontendId={response.id}
          task={response.task as KnownTaskType}
          isLoading={isLoading}
          completeTask={completeTask}
          skipTask={skipTask}
        />
      );
      break;
  }

  return (
    <>
      <Head>
        <title>{t(getTypeSafei18nKey(`${taskInfo.id}.label`))}</title>
        <meta name="description" content={t(getTypeSafei18nKey(`${taskInfo.id}.desc`))} />
      </Head>
      {body}
    </>
  );
};
