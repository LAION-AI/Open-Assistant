export interface Message {
  text: string;
  is_assistant: boolean;
  message_id: string;
}

export interface Conversation {
  messages: Message[];
}
