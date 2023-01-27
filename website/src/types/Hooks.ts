import { MutatorCallback, MutatorOptions } from "swr";

import { BaseTask, TaskResponse, TaskType } from "./Task";

type ConcreteTaskResponse = TaskResponse<BaseTask>;
type TaskError = { errorCode: number; message: string };

type Trigger = (
  extraArgument?: unknown,
  options?: MutatorOptions<ConcreteTaskResponse>
) => Promise<ConcreteTaskResponse>;

type Reset = (
  data?: ConcreteTaskResponse | Promise<ConcreteTaskResponse> | MutatorCallback<ConcreteTaskResponse>,
  opts?: boolean | MutatorOptions<ConcreteTaskResponse>
) => Promise<ConcreteTaskResponse>;

type TaskAPIHook = {
  tasks: TaskResponse<BaseTask>[];
  isLoading: boolean;
  error: TaskError;
  trigger: Trigger;
  reset: Reset;
};

export type TaskApiHooks = Record<TaskType, (args: TaskType) => TaskAPIHook>;
