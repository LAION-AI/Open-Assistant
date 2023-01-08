import { TaskResponse } from "../useGenericTaskAPI";
import { LabelingTaskType, useLabelingTask } from "./useLabelingTask";

export interface LabelInitialPromptTask {
  id: string;
  type: LabelingTaskType.label_initial_prompt;
  message_id: string;
  valid_labels: string[];
  prompt: string;
}

export type LabelInitialPromptTaskResponse = TaskResponse<LabelInitialPromptTask>;

export const useLabelInitialPromptTask = () =>
  useLabelingTask<LabelInitialPromptTask>(LabelingTaskType.label_initial_prompt);
