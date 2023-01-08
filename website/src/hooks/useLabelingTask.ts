import { useEffect, useState } from "react";
import fetcher from "src/lib/fetcher";
import poster from "src/lib/poster";
import useSWRImmutable from "swr/immutable";
import useSWRMutation from "swr/mutation";

// TODO: type & centralize types for all tasks
interface TaskResponse<TaskType> {
  id: string;
  userId: string;
  task: TaskType;
}

export interface LabelInitialPromptTask {
  id: string;
  message_id: string;
  prompt: string;
  type: string;
  valid_labels: string[];
}

export type LabelInitialPromptTaskResponse = TaskResponse<LabelInitialPromptTask>;

export const useLabelingTask = <LabelingTaskType>({ taskApiEndpoint }: { taskApiEndpoint: "label_initial_prompt" }) => {
  type ConcreteTaskResponse = TaskResponse<LabelingTaskType>;

  const [tasks, setTasks] = useState<Array<ConcreteTaskResponse>>([]);

  const { isLoading, mutate, error } = useSWRImmutable("/api/new_task/" + taskApiEndpoint, fetcher, {
    onSuccess: (data: ConcreteTaskResponse) => {
      setTasks([data]);
    },
  });

  useEffect(() => {
    if (tasks.length === 0 && !isLoading && !error) {
      mutate();
    }
  }, [tasks, isLoading, mutate, error]);

  const { trigger } = useSWRMutation("/api/update_task", poster, {
    onSuccess: async (reply) => {
      const newTask: ConcreteTaskResponse = await reply.json();
      setTasks((oldTasks) => [...oldTasks, newTask]);
    },
  });

  const submit = (id: string, message_id: string, text: string, labels: Record<string, string>) =>
    trigger({ id, update_type: "text_labels", content: { labels, text, message_id } });

  return { tasks, isLoading, submit, error, reset: mutate };
};
