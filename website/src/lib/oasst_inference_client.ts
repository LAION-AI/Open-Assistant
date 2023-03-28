import axios, { AxiosInstance, AxiosRequestConfig } from "axios";
import type { JWT } from "next-auth/jwt";
import {
  ChatItem,
  GetChatsResponse,
  InferenceMessage,
  InferencePostAssistantMessageParams,
  InferencePostPrompterMessageParams,
  ModelInfo,
} from "src/types/Chat";

import { INFERNCE_TOKEN_KEY } from "./oasst_inference_auth";

function getCookieFromDocument(name: string) {
  const cookies = document.cookie.split("; ");
  for (const cookie of cookies) {
    const [cookieName, cookieValue] = cookie.split("=");
    if (cookieName === name) {
      return cookieValue;
    }
  }
  return undefined;
}
export class OasstInferenceClient {
  private axios: AxiosInstance = axios.create({
    baseURL: process.env.INFERENCE_SERVER_HOST,
    headers: {
      "Content-Type": "application/json",
    },
  });

  async request<T = unknown>(path: string, init?: AxiosRequestConfig) {
    console.log(this.axios.defaults.baseURL);
    if (typeof document === "undefined") {
      throw new Error("request should not be called on the server side");
    }

    const inferenceAccessToken = getCookieFromDocument(INFERNCE_TOKEN_KEY);

    const { data } = await this.axios<T>(path, {
      ...init,
      headers: {
        ...init?.headers,
        Authorization: `Bearer ${inferenceAccessToken}`,
      },
      baseURL: process.env.INFERENCE_SERVER_HOST,
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

  get_my_chats(): Promise<GetChatsResponse> {
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
    // axios not support stream in browser
    return fetch(`${process.env.INFERENCE_SERVER_HOST}/chats/${chat_id}/messages/${message_id}/events`, {
      headers: {
        Authorization: `Bearer ${getCookieFromDocument(INFERNCE_TOKEN_KEY)}`,
        Connection: "keep-alive",
        "Content-Type": "text/event-stream",
        "Cache-Control": "no-cache",
      },
    });
  }

  vote({ chat_id, message_id, score }: { chat_id: string; message_id: string; score: number }) {
    return this.request(`/chats/${chat_id}/messages/${message_id}/votes`, { method: "POST", data: { score } });
  }

  async get_models() {
    const res = await this.axios<ModelInfo[]>("/configs/model_configs");
    return res.data;
  }

  async get_providers() {
    const res = await this.axios<string[]>("/auth/providers");
    return res.data;
  }
}

export const createInferenceClient = (jwt: JWT) => {
  const token = jwt.inferenceTokens?.access_token.access_token;
  return new OasstInferenceClient(token);
};

export const inferenceClient = new OasstInferenceClient();
