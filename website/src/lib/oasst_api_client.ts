import type { Message } from "src/types/Conversation";
import { LeaderboardReply, LeaderboardTimeFrame } from "src/types/Leaderboard";
import type { AvailableTasks } from "src/types/Task";
import type { BackendUser, BackendUserCore, FetchUsersParams, FetchUsersResponse } from "src/types/Users";

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
  oasstApiUrl: string;
  oasstApiKey: string;

  constructor(oasstApiUrl: string, oasstApiKey: string) {
    this.oasstApiUrl = oasstApiUrl;
    this.oasstApiKey = oasstApiKey;
  }
  // TODO return a strongly typed Task?
  // This method is used to store a task in RegisteredTask.task.
  // This is a raw Json type, so we can't use it to strongly type the task.
  async fetchTask(taskType: string, user: BackendUserCore, lang: string): Promise<any> {
    return this.post("/api/v1/tasks/", {
      type: taskType,
      user,
      lang,
    });
  }

  async ackTask(taskId: string, messageId: string): Promise<null> {
    return this.post(`/api/v1/tasks/${taskId}/ack`, {
      message_id: messageId,
    });
  }

  async nackTask(taskId: string, reason: string): Promise<null> {
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
    user: BackendUserCore,
    lang: string
  ): Promise<any> {
    return this.post("/api/v1/tasks/interaction", {
      type: updateType,
      user,
      task_id: taskId,
      message_id: messageId,
      user_message_id: userMessageId,
      lang,
      ...content,
    });
  }

  /**
   * Returns the tasks availability information for given `user`.
   */
  async fetch_tasks_availability(user: object): Promise<AvailableTasks | null> {
    return this.post<AvailableTasks>("/api/v1/tasks/availability", user);
  }

  /**
   * Returns the message stats from the backend.
   */
  async fetch_stats(): Promise<any> {
    return this.get("/api/v1/stats/");
  }

  /**
   * Returns the tree manager stats from the backend.
   */
  async fetch_tree_manager(): Promise<any> {
    return this.get("/api/v1/stats/tree_manager");
  }

  /**
   * Returns the `BackendUser` associated with `user_id`
   */
  async fetch_user(user_id: string): Promise<BackendUser | null> {
    return this.get(`/api/v1/users/${user_id}`);
  }

  /**
   * Returns the set of `BackendUser`s stored by the backend.
   */
  async fetch_users({
    direction,
    limit,
    cursor,
    searchDisplayName,
    sortKey = "display_name",
  }: FetchUsersParams): Promise<FetchUsersResponse | null> {
    return this.get<FetchUsersResponse>(`/api/v1/users/cursor`, {
      search_text: searchDisplayName,
      sort_key: sortKey,
      max_count: limit,
      after: direction === "forward" ? cursor : undefined,
      before: direction === "back" ? cursor : undefined,
    });
  }

  /**
   * Returns the `Message`s associated with `user_id` in the backend.
   */
  async fetch_user_messages(user_id: string): Promise<Message[] | null> {
    return this.get<Message[]>(`/api/v1/users/${user_id}/messages`);
  }

  /**
   * Updates the backend's knowledge about the `user_id`.
   */
  async set_user_status(user_id: string, is_enabled: boolean, notes: string): Promise<void> {
    await this.put(`/api/v1/users/users/${user_id}?enabled=${is_enabled}&notes=${notes}`);
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
  async fetch_leaderboard(
    time_frame: LeaderboardTimeFrame,
    { limit = 20 }: { limit?: number }
  ): Promise<LeaderboardReply | null> {
    return this.get<LeaderboardReply>(`/api/v1/leaderboards/${time_frame}`, { max_count: limit });
  }

  /**
   * Returns the counts of all tasks (some might be zero)
   */
  async fetch_available_tasks(user: BackendUserCore, lang: string): Promise<AvailableTasks | null> {
    return this.post<AvailableTasks>(`/api/v1/tasks/availability?lang=${lang}`, user);
  }

  private async post<T>(path: string, body: unknown) {
    return this.request<T>("POST", path, {
      body: JSON.stringify(body),
    });
  }

  private async put<T>(path: string) {
    return this.request<T>("PUT", path);
  }

  private async get<T>(path: string, query?: Record<string, string | number | boolean | undefined>) {
    if (!query) {
      return this.request<T>("GET", path);
    }

    const filteredQuery = Object.fromEntries(
      Object.entries(query).filter(([, value]) => value !== undefined)
    ) as Record<string, string>;

    const params = new URLSearchParams(filteredQuery).toString();

    return this.request<T>("GET", `${path}?${params}`);
  }

  private async request<T>(method: "GET" | "POST" | "PUT", path: string, init?: RequestInit): Promise<T | null> {
    const resp = await fetch(`${this.oasstApiUrl}${path}`, {
      method,
      ...init,
      headers: {
        "X-API-Key": this.oasstApiKey,
        "Content-Type": "application/json",
        ...init?.headers,
      },
    });

    if (resp.status === 204) {
      return null;
    }

    if (resp.status >= 300) {
      const errorText = await resp.text();
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
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
}

const oasstApiClient = new OasstApiClient(process.env.FASTAPI_URL, process.env.FASTAPI_KEY);

export { oasstApiClient };
