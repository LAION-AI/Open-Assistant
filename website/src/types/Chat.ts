export interface InferenceToken {
  access_token: string;
  token_type: string;
}

export interface InferenceTokens {
  access_token: InferenceToken;
  refresh_token: InferenceToken;
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
  state: "manual" | "pending" | "complete" | "aborted_by_worker" | "cancelled";
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

export type ModelInfo = {
  name: string;
  description: string;
  parameter_configs: ModelParameterConfig[];
};

export type ModelParameterConfig = {
  name: string;
  description: string;
  work_parameters: WorkParametersInput;
};

export type WorkParametersInput = {
  model_name: string;
  top_k: number | null;
  top_p: number | null;
  temperature: number | null;
  repetition_penalty: number | null;
  max_new_tokens: number | null;
  typical_p: number | null;
};
