import { BaseTask, TaskResponse } from "src/types/Task";

export type TaskApiHook<Task extends BaseTask, ResponseContent> = {
  response: TaskResponse<Task>;
  isLoading: boolean;
  completeTask: (interaction: ResponseContent) => Promise<void>;
  rejectTask: () => Promise<void>;
  isSubmitting: boolean;
  isRejecting: boolean;
};
