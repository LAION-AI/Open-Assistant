import { BaseTask, TaskResponse, TaskType } from "src/types/Task";

import { AllTaskReplies } from "./TaskResponses";

export type TaskApiHook<Task extends BaseTask, ResponseContent> = {
  response: TaskResponse<Task>;
  isLoading: boolean;
  completeTask: (interaction: ResponseContent) => Promise<void>;
  rejectTask: () => Promise<void>;
};

export type TaskApiHooks = Record<TaskType, (args: TaskType) => TaskApiHook<BaseTask, AllTaskReplies>>;
