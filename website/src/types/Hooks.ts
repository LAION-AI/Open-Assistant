import { BaseTask, TaskContent, TaskResponse, TaskType } from "src/types/Task";

interface TaskInteraction {
  id: string;
  update_type: string;
  content: TaskContent;
}

export type TaskApiHook<Task extends BaseTask> = {
  response: TaskResponse<Task>;
  isLoading: boolean;
  completeTask: (interaction: TaskInteraction) => void;
  skipTask: () => void;
};

export type TaskApiHooks = Record<TaskType, (args: TaskType) => TaskApiHook<BaseTask>>;
