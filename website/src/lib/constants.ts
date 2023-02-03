import {
  useCreateAssistantReply,
  useCreateInitialPrompt,
  useCreatePrompterReply,
} from "src/hooks/tasks/useCreateReply";
import {
  useRankAssistantRepliesTask,
  useRankInitialPromptsTask,
  useRankPrompterRepliesTask,
} from "src/hooks/tasks/useEvaluateReplies";
import { useGenericTaskAPI } from "src/hooks/tasks/useGenericTaskAPI";
import {
  useLabelAssistantReplyTask,
  useLabelInitialPromptTask,
  useLabelPrompterReplyTask,
} from "src/hooks/tasks/useLabelingTask";
import { TaskApiHooks } from "src/types/Hooks";
import { TaskType } from "src/types/Task";

export const ERROR_CODES = {
  TASK_REQUESTED_TYPE_NOT_AVAILABLE: 1006,
  TASK_INVALID_REQUEST_TYPE: 1000,
  TASK_ACK_FAILED: 1001,
  TASK_NACK_FAILED: 1002,
  TASK_INVALID_RESPONSE_TYPE: 1003,
  TASK_INTERACTION_REQUEST_FAILED: 1004,
  TASK_GENERATION_FAILED: 1005,
  TASK_AVAILABILITY_QUERY_FAILED: 1007,
  TASK_MESSAGE_TOO_LONG: 1008,
};

export const taskApiHooks: TaskApiHooks = {
  [TaskType.random]: useGenericTaskAPI,
  [TaskType.assistant_reply]: useCreateAssistantReply,
  [TaskType.initial_prompt]: useCreateInitialPrompt,
  [TaskType.label_assistant_reply]: useLabelAssistantReplyTask,
  [TaskType.label_initial_prompt]: useLabelInitialPromptTask,
  [TaskType.label_prompter_reply]: useLabelPrompterReplyTask,
  [TaskType.prompter_reply]: useCreatePrompterReply,
  [TaskType.rank_assistant_replies]: useRankAssistantRepliesTask,
  [TaskType.rank_initial_prompts]: useRankInitialPromptsTask,
  [TaskType.rank_prompter_replies]: useRankPrompterRepliesTask,
};
