export interface InferenceDebugTokenResponse {
  access_token: string;
  token_type: string;
}

export interface InferenceCreateChatResponse {
  id: string;
}

export interface InferenceResponse {
  assistant_message: InferenceMessage;
  prompter_message: InferenceMessage;
}

export interface InferenceMessage {
  id: string;
  content: string | null;
  state: "manual" | "pending";
  role: "assistant" | "prompter";
}
