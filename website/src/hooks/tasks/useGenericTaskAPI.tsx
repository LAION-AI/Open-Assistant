import { useState } from "react";
import { get, post } from "src/lib/api";
import { TaskApiHook } from "src/types/Hooks";
import { BaseTask, TaskAvailableResponse, TaskResponse, TaskType as TaskTypeEnum } from "src/types/Task";
import useSWRImmutable from "swr/immutable";
import useSWRMutation from "swr/mutation";

export const useGenericTaskAPI = <TaskType extends BaseTask>(taskType: TaskTypeEnum): TaskApiHook<TaskType> => {
  const [response, setReponse] = useState<TaskResponse<TaskType>>({ taskAvailability: "AWAITING_INITIAL" });
  // Note: We use isValidating to indiate we are loading beause it signals eash load, not just the first one.
  const { isValidating: isLoading, mutate: requestNewTask } = useSWRImmutable<TaskAvailableResponse<TaskType>>(
    "/api/new_task/" + taskType,
    get,
    {
      onSuccess: (response) => {
        setReponse({ taskAvailability: "AVAILABLE", ...response });
      },
      onError: () => {
        // We could check for code 503 here for truely unavailable, but we need to do something with other errors anyway.
        setReponse({ taskAvailability: "NONE_AVAILABLE" });
      },
      revalidateOnMount: true,
      dedupingInterval: 500,
    }
  );

  const { trigger: completeTask } = useSWRMutation<TaskAvailableResponse<TaskType>>("/api/update_task", post, {
    onSuccess: () => {
      requestNewTask();
    },
    onError: () => {
      // We could check for code 503 here for truely unavailable, but we need to do something with other errors anyway.
      setReponse({ taskAvailability: "NONE_AVAILABLE" });
    },
  });

  return { response, isLoading, completeTask, skipTask: requestNewTask };
};
