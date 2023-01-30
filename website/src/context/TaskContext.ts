import { createContext, useContext } from "react";
import { TaskApiHook } from "src/types/Hooks";
import { BaseTask, TaskInfo } from "src/types/Task";

export interface TaskContextType<Task extends BaseTask, ResponseContent>
  extends Omit<TaskApiHook<Task, ResponseContent>, "response"> {
  task: Task;
  taskInfo: TaskInfo;
}

export const TaskContext = createContext<TaskContextType<BaseTask, unknown>>(null);

export const useTaskContext = () => useContext(TaskContext);
