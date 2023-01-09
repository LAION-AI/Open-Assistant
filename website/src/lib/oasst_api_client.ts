import { JWT } from "next-auth/jwt";

declare global {
  // eslint-disable-next-line no-var
  var oasstApiClient: OasstApiClient | undefined;
}

export class OasstError {
  message: string;
  errorCode: number;
  httpStatusCode: number;

  constructor(message: string, errorCode: number, httpStatusCode: number) {
    this.message = message;
    this.errorCode = errorCode;
    this.httpStatusCode = httpStatusCode;
  }
}

export class OasstApiClient {
  constructor(private readonly oasstApiUrl: string, private readonly oasstApiKey: string) {}

  private async post(path: string, body: any): Promise<any> {
    const resp = await fetch(`${this.oasstApiUrl}${path}`, {
      method: "POST",
      headers: {
        "X-API-Key": this.oasstApiKey,
        "Content-Type": "application/json",
      },
      body: JSON.stringify(body),
    });

    if (resp.status == 204) {
      return null;
    }

    if (resp.status >= 300) {
      const errorText = await resp.text();
      let error: any;
      try {
        error = JSON.parse(errorText);
      } catch (e) {
        throw new OasstError(errorText, 0, resp.status);
      }
      throw new OasstError(error.message ?? error, error.error_code, resp.status);
    }

    return await resp.json();
  }

  // TODO return a strongly typed Task?
  // This method is used to store a task in RegisteredTask.task.
  // This is a raw Json type, so we can't use it to strongly type the task.
  async fetchTask(taskType: string, userToken: JWT): Promise<any> {
    return this.post("/api/v1/tasks/", {
      type: taskType,
      user: {
        id: userToken.sub,
        display_name: userToken.name || userToken.email,
        auth_method: "local",
      },
    });
  }

  async ackTask(taskId: string, messageId: string): Promise<void> {
    return this.post(`/api/v1/tasks/${taskId}/ack`, {
      message_id: messageId,
    });
  }

  async nackTask(taskId: string, reason: string): Promise<void> {
    return this.post(`/api/v1/tasks/${taskId}/nack`, {
      reason,
    });
  }

  // TODO return a strongly typed Task?
  // This method is used to record interaction with task while fetching next task.
  // This is a raw Json type, so we can't use it to strongly type the task.
  async interactTask(
    updateType: string,
    messageId: string,
    userMessageId: string,
    content: object,
    userToken: JWT
  ): Promise<any> {
    return this.post("/api/v1/tasks/interaction", {
      type: updateType,
      user: {
        id: userToken.sub,
        display_name: userToken.name || userToken.email,
        auth_method: "local",
      },
      message_id: messageId,
      user_message_id: userMessageId,
      ...content,
    });
  }
}

export const oasstApiClient =
  globalThis.oasstApiClient || new OasstApiClient(process.env.FASTAPI_URL, process.env.FASTAPI_KEY);
if (process.env.NODE_ENV !== "production") {
  globalThis.oasstApiClient = oasstApiClient;
}
