import { useGenericTaskAPI } from "../useGenericTaskAPI";

interface RankInitialPromptsTask {
  id: string;
  type: "rank_initial_prompts";
  prompts: string[];
}

export const useRankInitialPromptsTask = () => useGenericTaskAPI<RankInitialPromptsTask>("rank_initial_prompts");
