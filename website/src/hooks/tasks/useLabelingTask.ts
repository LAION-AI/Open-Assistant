import { TaskType } from "src/types/Task";
import { LabelAssistantReplyTask, LabelInitialPromptTask, LabelPrompterReplyTask } from "src/types/Tasks";

import { useGenericTaskAPI } from "./useGenericTaskAPI";

export const useLabelAssistantReplyTask = () =>
  useGenericTaskAPI<LabelAssistantReplyTask>(TaskType.label_assistant_reply);
export const useLabelInitialPromptTask = () => useGenericTaskAPI<LabelInitialPromptTask>(TaskType.label_initial_prompt);
export const useLabelPrompterReplyTask = () => useGenericTaskAPI<LabelPrompterReplyTask>(TaskType.label_prompter_reply);
