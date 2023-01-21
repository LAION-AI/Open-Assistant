import type { Message } from "src/types/Conversation";
import { LeaderboardReply, LeaderboardTimeFrame } from "src/types/Leaderboard";
import type { AvailableTasks } from "src/types/Task";
import type { BackendUser, BackendUserCore } from "src/types/Users";

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

export class OasstApiClient {
  oasstApiUrl: string;
  oasstApiKey: string;

  constructor(oasstApiUrl: string, oasstApiKey: string) {
    this.oasstApiUrl = oasstApiUrl;
    this.oasstApiKey = oasstApiKey;
  }

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

  private async put(path: string): Promise<any> {
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
  async fetchTask(taskType: string, user: BackendUserCore): Promise<any> {
    return this.post("/api/v1/tasks/", {
      type: taskType,
      user,
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
    user: BackendUserCore
  ): Promise<any> {
    return this.post("/api/v1/tasks/interaction", {
      type: updateType,
      user,
      task_id: taskId,
      message_id: messageId,
      user_message_id: userMessageId,
      ...content,
    });
  }

  /**
   * Returns the `BackendUser` associated with `user_id`
   */
  async fetch_user(user_id: string): Promise<BackendUser> {
    return this.get(`/api/v1/users/${user_id}`);
  }

  /**
   * Returns the set of `BackendUser`s stored by the backend.
   *
   * @param {number} max_count - The maximum number of users to fetch.
   * @param {string} cursor - The user's `display_name` to use when paginating.
   * @param {boolean} isForward - If true and `cursor` is not empty, pages
   *        forward.  If false and `cursor` is not empty, pages backwards.
   * @returns {Promise<BackendUser[]>} A Promise that returns an array of `BackendUser` objects.
   */
  async fetch_users(max_count: number, cursor: string, isForward: boolean): Promise<BackendUser[]> {
    const params = new URLSearchParams();
    params.append("max_count", max_count.toString());

    // The backend API uses different query parameters depending on the
    // pagination direction but they both take the same cursor value.
    // Depending on direction, pick the right query param.
    if (cursor !== "") {
      params.append(isForward ? "gt" : "lt", cursor);
    }
    const BASE_URL = `/api/v1/frontend_users`;
    const url = `${BASE_URL}/?${params.toString()}`;
    return this.get(url);
  }

  /**
   * Returns the `Message`s associated with `user_id` in the backend.
   */
  async fetch_user_messages(user_id: string): Promise<Message[]> {
    return this.get(`/api/v1/users/${user_id}/messages`);
  }

  /**
   * Updates the backend's knowledge about the `user_id`.
   */
  async set_user_status(user_id: string, is_enabled: boolean, notes): Promise<void> {
    return this.put(`/api/v1/users/users/${user_id}?enabled=${is_enabled}&notes=${notes}`);
  }

  /**
   * Returns the valid labels for messages.
   */
  async fetch_valid_text(): Promise<any> {
    return this.get(`/api/v1/text_labels/valid_labels`);
  }

  /**
   * Returns the current leaderboard ranking.
   */
  async fetch_leaderboard(time_frame: LeaderboardTimeFrame): Promise<LeaderboardReply> {
    return this.get(`/api/v1/leaderboards/${time_frame}`);
  }

  /**
   * Returns the counts of all tasks (some might be zero)
   */
  async fetch_available_tasks(user: BackendUserCore): Promise<AvailableTasks> {
    return this.post(`/api/v1/tasks/availability`, user);
  }
}

const oasstApiClient = new OasstApiClient(process.env.FASTAPI_URL, process.env.FASTAPI_KEY);

export { oasstApiClient };
