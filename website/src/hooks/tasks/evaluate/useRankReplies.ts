import { useGenericTaskAPI } from "../useGenericTaskAPI";

interface BaseRankRepliesTask {
  id: string;
  replies: string[];
  conversation: {
    messages: Array<{
      text: string;
      is_assistant: boolean;
      message_id: string;
    }>;
  };
}

interface RankAssistantRepliesTask extends BaseRankRepliesTask {
  type: "rank_assistant_replies";
}

interface RankPrompterRepliesTask extends BaseRankRepliesTask {
  type: "rank_prompter_replies";
}

export const useRankAssistantRepliesTask = () => useGenericTaskAPI<RankAssistantRepliesTask>("rank_assistant_replies");

export const useRankPrompterRepliesTask = () => useGenericTaskAPI<RankPrompterRepliesTask>("rank_prompter_replies");
