import { TaskType } from "src/types/Task";
import { CreateAssistantReplyTask, CreateInitialPromptTask, CreatePrompterReplyTask } from "src/types/Tasks";

import { useGenericTaskAPI } from "./useGenericTaskAPI";

export const useCreateAssistantReply = () => useGenericTaskAPI<CreateAssistantReplyTask>(TaskType.assistant_reply);
export const useCreatePrompterReply = () => useGenericTaskAPI<CreatePrompterReplyTask>(TaskType.prompter_reply);
export const useCreateInitialPrompt = () => useGenericTaskAPI<CreateInitialPromptTask>(TaskType.initial_prompt);
