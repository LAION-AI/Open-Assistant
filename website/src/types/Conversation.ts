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
  text: string;
  is_assistant: boolean;
  id: string;
  created_date: string; // iso date string
  lang: string;
  frontend_message_id?: string;
}

export interface Conversation {
  messages: Message[];
}
