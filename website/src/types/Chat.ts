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

export interface InferenceMessage {
  id: string;
  parent_id: string | null;
  created_at: string; //timestamp
  content: string | null;
  state: "manual" | "pending" | "in_progress" | "complete" | "aborted_by_worker" | "cancelled" | "timeout";
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
  error: string;
  message: InferenceMessage | null;
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
  sampling_parameters: SamplingParameters;
};

export interface SamplingParameters {
  max_new_tokens: number | null;
  repetition_penalty: number | null;
  temperature: number | null;
  typical_p: number | null;
  top_k: number | null;
  top_p: number | null;
}

export interface ChatConfigForm extends SamplingParameters {
  model_config_name: string; // this is the same as ModelParameterConfig.name
}

export interface InferencePostPrompterMessageParams {
  chat_id: string;
  parent_id: string | null;
  content: string;
}

export interface InferencePostAssistantMessageParams {
  chat_id: string;
  parent_id: string;
  model_config_name: string;
  sampling_parameters: SamplingParameters;
}
