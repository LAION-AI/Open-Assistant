import axios, { AxiosError, AxiosRequestConfig } from "axios";
import {
  ChatItem,
  InferenceMessage,
  InferencePostAssistantMessageParams,
  InferencePostPrompterMessageParams,
  ModelInfo,
  TrustedClient,
} from "./types.js";
import type { Readable } from "stream";

export class OasstInferenceClient {
  // this is not a long lived class, this is why the token is immutable
  constructor(private readonly clientToken: string) {}

  async request<T = unknown>(path: string, init?: AxiosRequestConfig) {
    const { data } = await axios<T>(process.env.INFERENCE_SERVER_HOST + path, {
      ...init,
      headers: {
        ...init?.headers,
        "Content-Type": "application/json",
        TrustedClient: this.clientToken,
        // add cors headers to change the origin to the inference server
        // this is needed because the inference server is not on the same domain as the website
      },
    });
    return data;
  }

  inference_login() {
    return this.request("/auth/trusted", { method: "POST" });
  }

  get_my_chats(): Promise<ChatItem[]> {
    return this.request("/chats");
  }

  async create_chat(): Promise<ChatItem> {
    const create = () =>
      this.request<ChatItem>("/chats", { method: "POST", data: "" });
    try {
      return await create();
    } catch (err: any) {
      if (err instanceof AxiosError && err.response.status === 500) {
        // if we get an error here, the user might not yet exist in the inference database, which is why we try to create
        // user once (it won't do anything if the user already exists) and then retry the chat creation again.
        // the current inference server does not check for user existence before trying to insert a message into
        // the database, which is why we get a 500 instead of what I expect to be 404, we should fix this later

        // this is maybe not the cleanest solution, but otherwise we would have to sign up all users of the website
        // to inference automatically, which is maybe an overkill
        console.log("here");
        await this.inference_login();
        return create();
      } else {
        throw err;
      }
    }
  }

  get_chat(chat_id: string): Promise<ChatItem> {
    return this.request(`/chats/${chat_id}`);
  }

  get_message(chat_id: string, message_id: string): Promise<InferenceMessage> {
    return this.request(`/chats/${chat_id}/messages/${message_id}`);
  }

  post_prompter_message({
    chat_id,
    ...data
  }: InferencePostPrompterMessageParams): Promise<InferenceMessage> {
    return this.request(`/chats/${chat_id}/prompter_message`, {
      method: "POST",
      data,
    });
  }

  post_assistant_message({
    chat_id,
    ...data
  }: InferencePostAssistantMessageParams): Promise<InferenceMessage> {
    return this.request(`/chats/${chat_id}/assistant_message`, {
      method: "POST",
      data,
    });
  }

  stream_events({
    chat_id,
    message_id,
  }: {
    chat_id: string;
    message_id: string;
  }) {
    return this.request<Readable>(
      `/chats/${chat_id}/messages/${message_id}/events`,
      {
        headers: {
          Accept: "text/event-stream",
          Connection: "keep-alive",
          "Cache-Control": "no-cache, no-transform",
        },
        responseType: "stream",
      }
    );
  }

  vote({
    chat_id,
    message_id,
    score,
  }: {
    chat_id: string;
    message_id: string;
    score: number;
  }) {
    return this.request(`/chats/${chat_id}/messages/${message_id}/votes`, {
      method: "POST",
      data: { score },
    });
  }

  get_models() {
    return this.request<ModelInfo[]>("/configs/model_configs");
  }
}

export const createInferenceClient = (username, user_id) => {
  const info: TrustedClient = {
    api_key: process.env.INFERENCE_SERVER_API_KEY,
    client: "discord-bot",
    provider_account_id: user_id,
    user_id: user_id,
    username: username,
  };
  const token = Buffer.from(JSON.stringify(info)).toString("base64");
  return new OasstInferenceClient(token);
};
