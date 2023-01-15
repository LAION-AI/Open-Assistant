import { Conversation } from "./Conversation";
import { BaseTask, TaskType } from "./Task";

export interface CreateInitialPromptTask extends BaseTask {
  type: TaskType.initial_prompt;
  hint: string;
}

export interface CreateAssistantReplyTask extends BaseTask {
  type: TaskType.assistant_reply;
  conversation: Conversation;
}

export interface CreatePrompterReplyTask extends BaseTask {
  type: TaskType.prompter_reply;
  conversation: Conversation;
}

export interface RankInitialPromptsTask extends BaseTask {
  type: TaskType.rank_initial_prompts;
  prompts: string[];
}

export interface RankAssistantRepliesTask extends BaseTask {
  type: TaskType.rank_assistant_replies;
  conversation: Conversation;
  replies: string[];
}

export interface RankPrompterRepliesTask extends BaseTask {
  type: TaskType.rank_prompter_replies;
  conversation: Conversation;
  replies: string[];
}

export interface LabelAssistantReplyTask extends BaseTask {
  type: TaskType.label_assistant_reply;
  message_id: string;
  conversation: Conversation;
  reply: string;
  valid_labels: string[];
  mode: "simple" | "full";
  mandatory_labels?: string[];
}

export interface LabelPrompterReplyTask extends BaseTask {
  type: TaskType.label_prompter_reply;
  message_id: string;
  conversation: Conversation;
  reply: string;
  valid_labels: string[];
  mode: "simple" | "full";
  mandatory_labels?: string[];
}

export interface LabelInitialPromptTask extends BaseTask {
  type: TaskType.label_initial_prompt;
  message_id: string;
  valid_labels: string[];
  prompt: string;
}
