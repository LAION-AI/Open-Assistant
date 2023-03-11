export interface InferenceDebugTokenResponse {
  access_token: string;
  token_type: string;
}

export interface InferenceCreateChatResponse {
  id: string;
}

export interface InferencePostMessageResponse {
  assistant_message: InferenceMessage;
  prompter_message: InferenceMessage;
}

export interface InferenceMessage {
  id: string;
  content: string | null;
  state: "manual" | "pending";
  role: "assistant" | "prompter";
  score: number;
}

export interface GetChatsResponse {
  chats: InferenceCreateChatResponse[];
}

export interface ChatResponse {
  id: string;
  messages: InferenceMessage[];
}
