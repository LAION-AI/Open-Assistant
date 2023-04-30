import { BackendUser } from "./Users";

export type EmojiOp = "add" | "remove" | "toggle";

export interface MessageEmoji {
  name: string;
  count: number;
}

export interface MessageEmojis {
  emojis: { [emoji: string]: number };
  user_emojis: string[];
}

export interface Message extends MessageEmojis {
  id: string;
  text: string;
  is_assistant: boolean;
  lang: string;
  created_date: string; // iso date string
  parent_id: string | null;
  frontend_message_id?: string;
  user_id: string;
  user_is_author: boolean | null;
  deleted: boolean | null;
  synthetic: boolean | null;
  message_tree_id: string;
  ranking_count: number | null;
  rank: number | null;
  model_name: string | null;
  review_count: number | null;
  review_result: boolean; // false is spam
  user: BackendUser | null;
}

export interface Conversation {
  messages: Message[];
}

export type FetchMessagesCursorResponse = {
  next?: string;
  prev?: string;
  sort_key: string;
  items: Message[];
  order: "asc" | "desc";
};

export type MessageWithChildren = Message & {
  children: MessageWithChildren[];
};
