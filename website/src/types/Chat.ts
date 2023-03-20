export interface InferenceTokenResponse {
  access_token: string;
  token_type: string;
}

export interface ChatItem {
  id: string;
  created_at: string; //timestamp
  modified_at: string; //timestamp

  // those are not available when you first create a chat
  title?: string;
  messages?: InferenceMessage[];
}

export interface InferencePostMessageResponse {
  assistant_message: InferenceMessage;
  prompter_message: InferenceMessage;
}

export interface InferenceMessage {
  id: string;
  content: string | null;
  state: "manual" | "pending" | "aborted_by_worker";
  role: "assistant" | "prompter";
  score: number;
  reports: any[];
}

export interface GetChatsResponse {
  chats: ChatItem[];
}

// message events sent by the inference server
interface InferenceEventMessage {
  event_type: "message";
  message: InferenceMessage;
}
interface InferenceEventError {
  event_type: "error";
  data: string;
}

interface InferenceEventToken {
  event_type: "token";
  text: string;
}

interface InferenceEventPending {
  event_type: "pending";
  queue_position: number;
  queue_size: number;
}

export type InferenceEvent = InferenceEventMessage | InferenceEventError | InferenceEventToken | InferenceEventPending;
