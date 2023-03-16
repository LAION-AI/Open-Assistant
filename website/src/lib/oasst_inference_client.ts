/* eslint-disable @typescript-eslint/no-explicit-any */
import axios, { AxiosRequestConfig } from "axios";
import Cookies from "cookies";
import type { NextApiRequest, NextApiResponse } from "next";
import { JWT } from "next-auth/jwt";
import {
  ChatResponse,
  InferenceCreateChatResponse,
  InferenceDebugTokenResponse,
  InferenceMessage,
  InferencePostMessageResponse,
} from "src/types/Chat";

// TODO: this class could be structured better
export class OasstInferenceClient {
  private readonly cookies: Cookies;
  private inferenceToken: string;
  private readonly userTokenSub: string;

  constructor(req: NextApiRequest, res: NextApiResponse, token: JWT) {
    this.cookies = new Cookies(req, res);
    this.inferenceToken = this.cookies.get("inference_token");
    this.userTokenSub = token.sub;
  }

  async request<T = any>(method: "GET" | "POST" | "PUT" | "DELETE", path: string, init?: AxiosRequestConfig) {
    const token = await this.get_token();
    const { data } = await axios<T>(process.env.INFERENCE_SERVER_HOST + path, {
      method,
      ...init,
      headers: {
        ...init?.headers,
        Authorization: `Bearer ${token}`,
        "Content-Type": "application/json",
      },
    });
    return data;
  }

  async get_token() {
    // TODO: handle the case where the token is outdated and requires a refresh.
    if (this.inferenceToken) {
      return this.inferenceToken;
    }
    // we might want to include the inference token in our JWT, but this won't be trivial.
    // or we might have to force log-in the user every time a new JWT is created

    // TODO: we have not decided on a format for the user yet, this is here for debug only
    const res = await fetch(process.env.INFERENCE_SERVER_HOST + `/auth/login/debug?username=${this.userTokenSub}`);
    const inferenceResponse: InferenceDebugTokenResponse = await res.json();
    this.inferenceToken = inferenceResponse.access_token;
    this.cookies.set("inference_token", this.inferenceToken, {
      maxAge: 1000 * 60 * 5, // 5 minutes
    });
    // console.dir(this.inferenceToken);
    return this.inferenceToken;
  }

  get_my_chats() {
    return this.request("GET", "/chats");
  }

  create_chat(): Promise<InferenceCreateChatResponse> {
    return this.request("POST", "/chats", { data: "" });
  }

  get_chat(chat_id: string): Promise<ChatResponse> {
    return this.request("GET", `/chats/${chat_id}`);
  }

  post_prompt({
    chat_id,
    parent_id,
    content,
  }: {
    chat_id: string;
    parent_id: string | null;
    content: string;
  }): Promise<InferencePostMessageResponse> {
    return this.request("POST", `/chats/${chat_id}/messages`, {
      data: { parent_id, content },
    });
  }

  stream_events({ chat_id, message_id }: { chat_id: string; message_id: string }) {
    return this.request("GET", `/chats/${chat_id}/messages/${message_id}/events`, {
      headers: {
        Accept: "text/event-stream",
      },
      responseType: "stream",
    });
  }

  vote({ chat_id, message_id, score }: { chat_id: string; message_id: string; score: number }) {
    return this.request("POST", `/chats/${chat_id}/messages/${message_id}/votes`, { data: { score } });
  }
}
