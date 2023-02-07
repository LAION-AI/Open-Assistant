import { useGenericTaskAPI } from "src/hooks/tasks/useGenericTaskAPI";
import { TaskType } from "src/types/Task";
import { EvaluateTaskReply } from "src/types/TaskResponses";
import { RankAssistantRepliesTask, RankInitialPromptsTask, RankPrompterRepliesTask } from "src/types/Tasks";

export const useRankAssistantRepliesTask = () =>
  useGenericTaskAPI<RankAssistantRepliesTask, EvaluateTaskReply>(TaskType.rank_assistant_replies);

export const useRankPrompterRepliesTask = () =>
  useGenericTaskAPI<RankPrompterRepliesTask, EvaluateTaskReply>(TaskType.rank_prompter_replies);

export const useRankInitialPromptsTask = () =>
  useGenericTaskAPI<RankInitialPromptsTask, EvaluateTaskReply>(TaskType.rank_initial_prompts);
