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
  parent_id: string;
  frontend_message_id?: string;
  user_id: string;
}

export interface Conversation {
  messages: Message[];
}
