import { createContext, useContext } from "react";
import { TaskApiHook } from "src/types/Hooks";
import { BaseTask, TaskInfo } from "src/types/Task";
import { AllTaskReplies } from "src/types/TaskResponses";
import { KnownTaskType } from "src/types/Tasks";

export interface TaskContextType<Task extends BaseTask, ResponseContent>
  extends Omit<TaskApiHook<Task, ResponseContent>, "response"> {
  task: Task;
  taskInfo: TaskInfo;
}

export const TaskContext = createContext(null);

export const useTaskContext = () => useContext<TaskContextType<KnownTaskType, AllTaskReplies>>(TaskContext);
