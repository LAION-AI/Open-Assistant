import axios, { AxiosRequestConfig } from "axios";
import { JWT } from "next-auth/jwt";
import {
  ChatItem,
  InferenceMessage,
  InferencePostPrompterMessageParams,
  InferencePostAssistantMessageParams,
  ModelInfo,
} from "src/types/Chat";
import type { Readable } from "stream";

export class OasstInferenceClient {
  // this is not a long lived class, this is why the token is immutable
  constructor(private readonly inferenceAccessToken: string) {}

  async request<T = unknown>(path: string, init?: AxiosRequestConfig) {
    const { data } = await axios<T>(process.env.INFERENCE_SERVER_HOST + path, {
      ...init,
      headers: {
        ...init?.headers,
        Authorization: `Bearer ${this.inferenceAccessToken}`,
        "Content-Type": "application/json",
      },
    });
    return data;
  }

  // note: maybe check if the token is still valid
  // when creating JWT?
  async check_auth(): Promise<boolean> {
    try {
      await this.request("/auth/check");
      return true;
    } catch (err) {
      return false;
    }
  }

  get_my_chats(): Promise<ChatItem[]> {
    return this.request("/chats");
  }

  create_chat(): Promise<ChatItem> {
    return this.request("/chats", { method: "POST", data: "" });
  }

  get_chat(chat_id: string): Promise<ChatItem> {
    return this.request(`/chats/${chat_id}`);
  }

  get_message(chat_id: string, message_id: string): Promise<InferenceMessage> {
    return this.request(`/chats/${chat_id}/messages/${message_id}`);
  }

  post_prompter_message({ chat_id, ...data }: InferencePostPrompterMessageParams): Promise<InferenceMessage> {
    return this.request(`/chats/${chat_id}/prompter_message`, { method: "POST", data });
  }

  post_assistant_message({ chat_id, ...data }: InferencePostAssistantMessageParams): Promise<InferenceMessage> {
    return this.request(`/chats/${chat_id}/assistant_message`, { method: "POST", data });
  }

  stream_events({ chat_id, message_id }: { chat_id: string; message_id: string }) {
    return this.request<Readable>(`/chats/${chat_id}/messages/${message_id}/events`, {
      headers: {
        Accept: "text/event-stream",
        Connection: "keep-alive",
        "Cache-Control": "no-cache, no-transform",
      },
      responseType: "stream",
    });
  }

  vote({ chat_id, message_id, score }: { chat_id: string; message_id: string; score: number }) {
    return this.request(`/chats/${chat_id}/messages/${message_id}/votes`, { method: "POST", data: { score } });
  }

  get_models() {
    return this.request<ModelInfo[]>("/configs/model_configs");
  }
}

export const createInferenceClient = (jwt: JWT) => {
  const token = jwt.inferenceTokens?.access_token.access_token;
  return new OasstInferenceClient(token);
};
