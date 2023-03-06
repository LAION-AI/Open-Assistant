import { Conversation, Message } from "./Conversation";
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

export type CreateTaskType = CreateInitialPromptTask | CreateAssistantReplyTask | CreatePrompterReplyTask;

export interface RankInitialPromptsTask extends BaseTask {
  type: TaskType.rank_initial_prompts;
  prompts: string[];
  reveal_synthetic?: boolean;
}

export interface RankAssistantRepliesTask extends BaseTask {
  type: TaskType.rank_assistant_replies;
  conversation: Conversation;
  replies: string[];
  reply_messages: Message[];
  reveal_synthetic?: boolean;
}

export interface RankPrompterRepliesTask extends BaseTask {
  type: TaskType.rank_prompter_replies;
  conversation: Conversation;
  replies: string[];
  reply_messages: Message[]; // not tested
  reveal_synthetic?: boolean;
}

export type RankTaskType = RankInitialPromptsTask | RankAssistantRepliesTask | RankPrompterRepliesTask;

export interface Label {
  display_text: string;
  help_text: string;
  name: string;
  widget: "flag" | "yes_no" | "likert";
}

export interface BaseLabelTask extends BaseTask {
  message_id: string;
  conversation: Conversation;
  labels: Label[];
  valid_labels: string[];
  disposition: "spam" | "quality";
  mode: "simple" | "full";
  mandatory_labels?: string[];
}

export interface LabelAssistantReplyTask extends BaseLabelTask {
  type: TaskType.label_assistant_reply;
  reply_message: Message;
  reply: string;
}

export interface LabelPrompterReplyTask extends BaseLabelTask {
  type: TaskType.label_prompter_reply;
  reply_message: Message;
  reply: string;
}

export interface LabelInitialPromptTask extends BaseLabelTask {
  type: TaskType.label_initial_prompt;
  prompt: string;
}

export type LabelTaskType = LabelInitialPromptTask | LabelAssistantReplyTask | LabelPrompterReplyTask;

export type KnownTaskType = CreateTaskType | RankTaskType | LabelTaskType;
