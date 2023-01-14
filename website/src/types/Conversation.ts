export interface Message {
  text: string;
  is_assistant: boolean;
  id: string;
  frontend_message_id?: string;
}

export interface Conversation {
  messages: Message[];
}
