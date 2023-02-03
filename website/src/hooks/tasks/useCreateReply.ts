import { useGenericTaskAPI } from "src/hooks/tasks/useGenericTaskAPI";
import { TaskType } from "src/types/Task";
import { CreateTaskReply } from "src/types/TaskResponses";
import { CreateAssistantReplyTask, CreateInitialPromptTask, CreatePrompterReplyTask } from "src/types/Tasks";

export const useCreateAssistantReply = () =>
  useGenericTaskAPI<CreateAssistantReplyTask, CreateTaskReply>(TaskType.assistant_reply);
export const useCreatePrompterReply = () =>
  useGenericTaskAPI<CreatePrompterReplyTask, CreateTaskReply>(TaskType.prompter_reply);
export const useCreateInitialPrompt = () =>
  useGenericTaskAPI<CreateInitialPromptTask, CreateTaskReply>(TaskType.initial_prompt);
