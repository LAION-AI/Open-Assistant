import { useState } from "react";
import { get, post } from "src/lib/api";
import { BaseTask, TaskResponse, TaskType as TaskTypeEnum } from "src/types/Task";
import useSWRImmutable from "swr/immutable";
import useSWRMutation from "swr/mutation";

export const useGenericTaskAPI = <TaskType extends BaseTask>(taskType: TaskTypeEnum) => {
  type ConcreteTaskResponse = TaskResponse<TaskType>;

  const [tasks, setTasks] = useState<ConcreteTaskResponse[]>([]);

  const { isLoading, mutate, error } = useSWRImmutable<ConcreteTaskResponse>("/api/new_task/" + taskType, get, {
    onSuccess: (data) => setTasks([data]),
    revalidateOnMount: true,
    dedupingInterval: 500,
  });

  const { trigger } = useSWRMutation("/api/update_task", post, {
    onSuccess: async (newTask: ConcreteTaskResponse) => {
      setTasks((oldTasks) => [...oldTasks, newTask]);
      mutate();
    },
  });

  return { tasks, isLoading, trigger, error, reset: mutate };
};
