import { useState } from "react";
import fetcher from "src/lib/fetcher";
import poster from "src/lib/poster";
import useSWRImmutable from "swr/immutable";
import useSWRMutation from "swr/mutation";

// TODO: type & centralize types for all tasks

export interface TaskResponse<TaskType> {
  id: string;
  userId: string;
  task: TaskType;
}

export const useGenericTaskAPI = <TaskType,>(taskApiEndpoint: string) => {
  type ConcreteTaskResponse = TaskResponse<TaskType>;

  const [tasks, setTasks] = useState<ConcreteTaskResponse[]>([]);

  const { isLoading, mutate, error } = useSWRImmutable<ConcreteTaskResponse>(
    "/api/new_task/" + taskApiEndpoint,
    fetcher,
    {
      onSuccess: (data) => setTasks([data]),
      revalidateOnMount: true,
      dedupingInterval: 500,
    }
  );

  const { trigger } = useSWRMutation("/api/update_task", poster, {
    onSuccess: async (response) => {
      const newTask: ConcreteTaskResponse = await response.json();
      setTasks((oldTasks) => [...oldTasks, newTask]);
    },
  });

  return { tasks, isLoading, trigger, error, reset: mutate };
};
