import Head from "next/head";
import { useTranslation } from "next-i18next";
import { useMemo } from "react";
import { TaskEmptyState } from "src/components/EmptyState";
import { LoadingScreen } from "src/components/Loading/LoadingScreen";
import { Task } from "src/components/Tasks/Task";
import { TaskInfos } from "src/components/Tasks/TaskTypes";
import { TaskContext } from "src/context/TaskContext";
import { taskApiHooks } from "src/lib/constants";
import { getTypeSafei18nKey } from "src/lib/i18n";
import { TaskType } from "src/types/Task";

type TaskPageProps = {
  type: TaskType;
};

export const TaskPage = ({ type }: TaskPageProps) => {
  const { t } = useTranslation(["tasks", "common"]);
  const taskApiHook = useMemo(() => taskApiHooks[type], [type]);
  const hookState = taskApiHook(type);

  const body = useMemo(() => {
    const { response } = hookState;
    switch (response.taskAvailability) {
      case "AWAITING_INITIAL":
        return <LoadingScreen text={t("common:loading")} />;

      case "NONE_AVAILABLE":
        return <TaskEmptyState />;

      case "AVAILABLE": {
        const { task, taskInfo } = response;
        const context = { ...hookState, task, taskInfo };
        return (
          <TaskContext.Provider value={context}>
            <Task key={response.id} />
          </TaskContext.Provider>
        );
      }
    }
  }, [hookState, t]);

  // NOTE: this is independent of the fetched task type, it is usually identical, but not for the random task.
  const taskInfo = TaskInfos.find((taskType) => taskType.type === type);
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
