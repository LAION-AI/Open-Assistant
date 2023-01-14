import { JWT } from "next-auth/jwt";
import type { Message } from "src/types/Conversation";
import type { BackendUser } from "src/types/Users";

export class OasstError {
  message: string;
  errorCode: number;
  httpStatusCode: number;

  constructor(message: string, errorCode: number, httpStatusCode?: number) {
    this.message = message;
    this.errorCode = errorCode;
    this.httpStatusCode = httpStatusCode;
  }
}

/**
 * Reports the Backend's knowledge of a user.
 */
export interface BackendUser {
  /**
   * The user's unique ID according to the `auth_method`.
   */
  id: string;

  /**
   * The user's set name
   */
  display_name: string;

  /**
   * The authorization method.  One of:
   *   - discord
   *   - local
   */
  auth_method: string;

  /**
   * The backend's UUID for this user.
   */
  user_id: string;

  /**
   * Arbitrary notes about the user.
   */
  notes: string;

  /**
   * True when the user is able to access the platform.  False otherwise.
   */
  enabled: boolean;

  /**
   * True when the user is marked for deletion.  False otherwise.
   */
  deleted: boolean;
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

    if (resp.status === 204) {
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

  private async put(path: string, body: any): Promise<any> {
    const resp = await fetch(`${this.oasstApiUrl}${path}`, {
      method: "PUT",
      headers: {
        "X-API-Key": this.oasstApiKey,
      },
    });

    if (resp.status === 204) {
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

  private async get(path: string): Promise<any> {
    const resp = await fetch(`${this.oasstApiUrl}${path}`, {
      method: "GET",
      headers: {
        "X-API-Key": this.oasstApiKey,
        "Content-Type": "application/json",
      },
    });

    if (resp.status === 204) {
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
    taskId: string,
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
      task_id: taskId,
      message_id: messageId,
      user_message_id: userMessageId,
      ...content,
    });
  }

  async fetch_user(user_id: string): Promise<BackendUser> {
    return this.get(`/api/v1/users/users/${user_id}`);
  }

  async fetch_users(max_count: number): Promise<BackendUser[]> {
    return this.get(`/api/v1/frontend_users/?max_count=${max_count}`);
  }

  async fetch_user_messages(user_id: string): Promise<Message[]> {
    return this.get(`/api/v1/users/${user_id}/messages`);
  }

  async set_user_status(user_id: string, is_enabled: boolean, notes): Promise<void> {
    return this.put(`/api/v1/users/users/${user_id}?enabled=${is_enabled}&notes=${notes}`);
  }

  //Fetch valid labels. This is called every task. though the call may be redundant
  //keeping this for future where the valid labels may change per task
  async fetch_valid_text(): Promise<void> {
    return this.get(`/api/v1/text_labels/valid_labels`);
  }
}

const oasstApiClient = new OasstApiClient(process.env.FASTAPI_URL, process.env.FASTAPI_KEY);

export { oasstApiClient };
