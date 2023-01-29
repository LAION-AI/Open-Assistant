import { createContext, useContext } from "react";
import { TaskApiHook } from "src/types/Hooks";
import { BaseTask } from "src/types/Task";

export const TaskContext = createContext<TaskApiHook<BaseTask, unknown>>(null);

export const useTaskContext = () => useContext(TaskContext);
