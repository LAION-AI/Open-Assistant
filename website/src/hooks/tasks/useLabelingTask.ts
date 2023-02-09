import { useGenericTaskAPI } from "src/hooks/tasks/useGenericTaskAPI";
import { TaskType } from "src/types/Task";
import { LabelTaskReply } from "src/types/TaskResponses";
import { LabelAssistantReplyTask, LabelInitialPromptTask, LabelPrompterReplyTask } from "src/types/Tasks";

export const useLabelAssistantReplyTask = () =>
  useGenericTaskAPI<LabelAssistantReplyTask, LabelTaskReply>(TaskType.label_assistant_reply);
export const useLabelInitialPromptTask = () =>
  useGenericTaskAPI<LabelInitialPromptTask, LabelTaskReply>(TaskType.label_initial_prompt);
export const useLabelPrompterReplyTask = () =>
  useGenericTaskAPI<LabelPrompterReplyTask, LabelTaskReply>(TaskType.label_prompter_reply);
