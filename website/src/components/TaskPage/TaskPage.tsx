import Head from "next/head";
import { useTranslation } from "next-i18next";
import { TaskEmptyState } from "src/components/EmptyState";
import { LoadingScreen } from "src/components/Loading/LoadingScreen";
import { Task } from "src/components/Tasks/Task";
import { TaskInfos } from "src/components/Tasks/TaskTypes";
import { apiHooksByType, ERROR_CODES } from "src/lib/constants";
import { getTypeSafei18nKey } from "src/lib/i18n";
import { TaskType } from "src/types/Task";

type TaskPageProps = {
  type: TaskType;
};

export const TaskPage = ({ type }: TaskPageProps) => {
  const { t } = useTranslation(["tasks", "common"]);
  const apiHook = apiHooksByType[type];
  const { tasks, isLoading, reset, trigger, error } = apiHook(type);
  const taskInfo = TaskInfos.find((taskType) => taskType.type === type);

  if (isLoading) {
    return <LoadingScreen text={t("common:loading")} />;
  }

  if (tasks.length === 0 || error?.errorCode === ERROR_CODES.TASK_REQUESTED_TYPE_NOT_AVAILABLE) {
    return <TaskEmptyState />;
  }

  const task = tasks[0];

  return (
    <>
      <Head>
        <title>{t(getTypeSafei18nKey(`${taskInfo.id}.label`))}</title>
        <meta name="description" content={t(getTypeSafei18nKey(`${taskInfo.id}.desc`))} />
      </Head>
      <Task key={task.task.id} frontendId={task.id} task={task.task} trigger={trigger} mutate={reset} />
    </>
  );
};
