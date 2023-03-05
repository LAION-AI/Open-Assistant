import { useCallback, useState } from "react";
import { TaskInfos } from "src/components/Tasks/TaskTypes";
import { get, post } from "src/lib/api";
import { ERROR_CODES } from "src/lib/errors";
import { OasstError } from "src/lib/oasst_api_client";
import { API_ROUTES } from "src/lib/routes";
import { TaskApiHook } from "src/types/Hooks";
import { BaseTask, ServerTaskResponse, TaskResponse, TaskType as TaskTypeEnum } from "src/types/Task";
import { AllTaskReplies } from "src/types/TaskResponses";
import useSWRImmutable from "swr/immutable";
import useSWRMutation from "swr/mutation";

import { useCurrentLocale } from "../locale/useCurrentLocale";

export const useGenericTaskAPI = <TaskType extends BaseTask, ResponseContent = AllTaskReplies>(
  taskType: TaskTypeEnum
): TaskApiHook<TaskType, ResponseContent> => {
  const [response, setResponse] = useState<TaskResponse<TaskType>>({ taskAvailability: "AWAITING_INITIAL" });
  const locale = useCurrentLocale();
  // Note: We use isValidating to indicate we are loading because it signals eash load, not just the first one.
  const { isValidating: isLoading, mutate: requestNewTask } = useSWRImmutable<ServerTaskResponse<TaskType>>(
    API_ROUTES.NEW_TASK(taskType, { lang: locale }),
    get,
    {
      onSuccess: (taskResponse) => {
        setResponse({
          ...taskResponse,
          taskAvailability: "AVAILABLE",
          // eslint-disable-next-line @typescript-eslint/no-non-null-assertion
          taskInfo: TaskInfos.find((taskType) => taskType.type === taskResponse.task.type)!,
        });
      },
      onError: () => {
        // We could check for code 503 here for truly unavailable, but we need to do something with other errors anyway.
        setResponse({ taskAvailability: "NONE_AVAILABLE" });
      },
      revalidateOnMount: true,
      dedupingInterval: 500,
    }
  );

  const { trigger: sendTaskContent, isMutating: isSubmitting } = useSWRMutation(API_ROUTES.UPDATE_TASK, post, {
    onSuccess: () => {
      requestNewTask();
    },
    onError: (err: unknown) => {
      if (err instanceof OasstError && err.errorCode === ERROR_CODES.TASK_REQUESTED_TYPE_NOT_AVAILABLE) {
        setResponse({ taskAvailability: "NONE_AVAILABLE" });
      } else {
        // we should never reach here
        console.error(err);
      }
    },
  });

  // NOTE: it might make sense to split this hook into 2 parts

  // makes sure that requestNewTask is always called without parameters:
  const skipTask = useCallback(async () => {
    await requestNewTask();
  }, [requestNewTask]);

  const { trigger: sendRejection, isMutating: isRejecting } = useSWRMutation("/api/reject_task", post, {
    onSuccess: skipTask,
  });
  const rejectTask = useCallback(async () => {
    if (response.taskAvailability !== "AVAILABLE") {
      throw new Error("Cannot reject task that is not yet ready");
    }
    await sendRejection({ id: response.id });
  }, [response, sendRejection]);

  const completeTask = useCallback(
    async (content: ResponseContent) => {
      if (response.taskAvailability !== "AVAILABLE") {
        throw new Error("Cannot complete task that is not yet ready");
      }
      await sendTaskContent({ id: response.id, update_type: response.taskInfo.update_type, content, lang: locale });
    },
    [response, sendTaskContent, locale]
  );

  return { response, isLoading, rejectTask, completeTask, isRejecting, isSubmitting };
};
