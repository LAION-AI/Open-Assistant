import { useGenericTaskAPI } from "../useGenericTaskAPI";

interface BaseCreateReplyTask {
  id: string;
  conversation: {
    messages: Array<{
      text: string;
      is_assistant: boolean;
      message_id: string;
    }>;
  };
}

export interface CreateAssistantReplyTask extends BaseCreateReplyTask {
  type: "assistant_reply";
}

export interface CreatePrompterReplyTask extends BaseCreateReplyTask {
  type: "prompter_reply";
}

export const useCreateAssistantReply = () => useGenericTaskAPI<CreateAssistantReplyTask>("assistant_reply");

export const useCreatePrompterReply = () => useGenericTaskAPI<CreatePrompterReplyTask>("prompter_reply");
