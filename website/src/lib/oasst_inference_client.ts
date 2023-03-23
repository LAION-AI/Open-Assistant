import axios, { AxiosRequestConfig } from "axios";
import { JWT } from "next-auth/jwt";
import {
  ChatItem,
  InferenceMessage,
  InferencePostMessageResponse,
  ModelInfo,
  WorkParametersInput,
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

  post_prompt({
    chat_id,
    parent_id,
    content,
    work_parameters,
  }: {
    chat_id: string;
    parent_id: string | null;
    content: string;
    work_parameters: WorkParametersInput;
  }): Promise<InferencePostMessageResponse> {
    return this.request(`/chats/${chat_id}/messages`, {
      method: "POST",
      data: { parent_id, content, work_parameters },
    });
  }

  stream_events({ chat_id, message_id }: { chat_id: string; message_id: string }) {
    return this.request<Readable>(`/chats/${chat_id}/messages/${message_id}/events`, {
      headers: {
        Accept: "text/event-stream",
      },
      responseType: "stream",
    });
  }

  vote({ chat_id, message_id, score }: { chat_id: string; message_id: string; score: number }) {
    return this.request(`/chats/${chat_id}/messages/${message_id}/votes`, { method: "POST", data: { score } });
  }

  get_models() {
    return this.request<ModelInfo[]>("/configs/models");
  }
}

export const createInferenceClient = (jwt: JWT) => {
  const token = jwt.inferenceTokens?.access_token.access_token;
  return new OasstInferenceClient(token);
};
