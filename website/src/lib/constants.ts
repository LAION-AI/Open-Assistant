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
