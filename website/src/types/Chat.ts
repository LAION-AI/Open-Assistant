export interface TrustedClient {
  api_key: string;
  client: string;
  user_id: string;
  provider_account_id: string;
  username: string;
}

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
  messages: InferenceMessage[];
  allow_data_use: boolean;

  // those are not available when you first create a chat
  title?: string;
  hidden?: boolean;
  active_thread_tail_message_id?: string;
}

export interface InferenceMessage {
  id: string;
  chat_id: string;
  parent_id: string | null;
  created_at: string; //timestamp
  content: string | null;
  state: "manual" | "pending" | "in_progress" | "complete" | "aborted_by_worker" | "cancelled" | "timeout";
  role: "assistant" | "prompter";
  score: number;
  reports: any[];
  work_parameters?: {
    do_sample: boolean;
    seed: number;
    sampling_parameters: SamplingParameters;
    model_config: {
      model_id: string;
      max_input_length: number;
      max_total_length: number;
      quantized: boolean;
    };
    plugins: PluginEntry[];
  };
  used_plugin?: object | null;
}

export interface GetChatsResponse {
  chats: ChatItem[];
  next?: string;
  prev?: string;
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

interface InferenceEventPluginIntermediateStep {
  event_type: "plugin_intermediate";
  current_plugin_thought: string;
  current_plugin_action_taken: string;
  current_plugin_action_response: string;
  current_plugin_action_input: string;
}

export type InferenceEvent =
  | InferenceEventMessage
  | InferenceEventError
  | InferenceEventToken
  | InferenceEventPending
  | InferenceEventPluginIntermediateStep;

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

export interface ChatConfigFormData extends SamplingParameters {
  model_config_name: string; // this is the same as ModelParameterConfig.name
  plugins: PluginEntry[];
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
  plugins: PluginEntry[];
}

export interface InferenceUpdateChatParams {
  chat_id: string;
  title?: string;
  hidden?: boolean;
  active_thread_tail_message_id?: string;
}

export interface PluginEntry {
  url: string;
  enabled?: boolean;
  trusted?: boolean;
  spec?: object | null;
  plugin_config?: PluginConfig | null;
}

export interface PluginApiType {
  type: string;
  url: string;
  has_user_authentication: boolean | null;
  // NOTE: Some plugins using this field,
  // instead of has_user_authentication
  is_user_authenticated: boolean | null;
}

export interface PluginAuthType {
  type: string;
}

export interface PluginOpenAPIEndpoint {
  path: string;
  type: string;
  summary: string;
  operation_id: string;
  url: string;
  params: PluginOpenAPIParameter[];
}

export interface PluginOpenAPIParameter {
  name: string;
  in_: string;
  description: string;
  required: boolean;
  schema_: object;
}

export interface PluginConfig {
  schema_version: string;
  name_for_model: string;
  name_for_human: string;
  description_for_human: string;
  description_for_model: string;
  api: PluginApiType;
  auth: PluginAuthType;
  logo_url?: string | null;
  contact_email: string | null;
  legal_info_url: string | null;
  endpoints: PluginOpenAPIEndpoint[] | null;
}

export interface GetChatsParams {
  limit?: number;
  before?: string;
  after?: string;
  include_hidden?: string;
}
