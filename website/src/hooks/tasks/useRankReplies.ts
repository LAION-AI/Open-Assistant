import { TaskType } from "src/types/Task";
import { RankAssistantRepliesTask, RankInitialPromptsTask, RankPrompterRepliesTask } from "src/types/Tasks";

import { useGenericTaskAPI } from "./useGenericTaskAPI";

export const useRankAssistantRepliesTask = () =>
  useGenericTaskAPI<RankAssistantRepliesTask>(TaskType.rank_assistant_replies);

export const useRankPrompterRepliesTask = () =>
  useGenericTaskAPI<RankPrompterRepliesTask>(TaskType.rank_prompter_replies);

export const useRankInitialPromptsTask = () => useGenericTaskAPI<RankInitialPromptsTask>(TaskType.rank_initial_prompts);
