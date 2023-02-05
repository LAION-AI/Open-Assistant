import type { EmojiOp, Message } from "src/types/Conversation";
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

  toString() {
    return JSON.stringify(this);
  }
}

export class OasstApiClient {
  oasstApiUrl: string;
  oasstApiKey: string;
  userHeaders: Record<string, string> = {};

  constructor(oasstApiUrl: string, oasstApiKey: string, user?: BackendUserCore) {
    this.oasstApiUrl = oasstApiUrl;
    this.oasstApiKey = oasstApiKey;
    if (user) {
      this.userHeaders = {
        "X-OASST-USER": `${user.auth_method}:${user.id}`,
      };
    }
  }

  private async request<T>(
    method: "GET" | "POST" | "PUT" | "DELETE",
    path: string,
    init?: RequestInit
  ): Promise<T | null> {
    const resp = await fetch(`${this.oasstApiUrl}${path}`, {
      method,
      ...init,
      headers: {
        ...init?.headers,
        ...this.userHeaders,
        "X-API-Key": this.oasstApiKey,
        "Content-Type": "application/json",
      },
    });

    if (resp.status === 204) {
      return null;
    }

    if (resp.status >= 300) {
      const errorText = await resp.text();
      let error;
      try {
        error = JSON.parse(errorText);
      } catch (e) {
        throw new OasstError(errorText, 0, resp.status);
      }
      throw new OasstError(error.message ?? error, error.error_code, resp.status);
    }

    return resp.json();
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

  private async delete<T>(path: string) {
    return this.request<T>("DELETE", path);
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
    return this.post(`/api/v1/tasks/${taskId}/ack`, { message_id: messageId });
  }

  async nackTask(taskId: string, reason: string): Promise<null> {
    return this.post(`/api/v1/tasks/${taskId}/nack`, { reason });
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

  fetch_full_settings() {
    return this.get<Record<string, any>>("/api/v1/admin/backend_settings/full");
  }

  fetch_public_settings() {
    return this.get<Record<string, any>>("/api/v1/admin/backend_settings/public");
  }

  /**
   * Returns the tasks availability information for given `user`.
   */
  async fetch_tasks_availability(user: object): Promise<AvailableTasks | null> {
    return this.post<AvailableTasks>("/api/v1/tasks/availability", user);
  }

  /**
   * Returns the `Message`s associated with `user_id` in the backend.
   */
  async fetch_message(message_id: string, user: BackendUserCore): Promise<Message> {
    return this.get<Message>(`/api/v1/messages/${message_id}?username=${user.id}&auth_method=${user.auth_method}`);
  }

  /**
   * Delete a message by its id
   */
  async delete_message(message_id: string): Promise<void> {
    return this.delete<void>(`/api/v1/messages/${message_id}`);
  }

  /**
   * Stop message tree
   */
  async stop_tree(message_id: string): Promise<void> {
    return this.put<void>(`/api/v1/messages/${message_id}/tree/state?halt=true`);
  }

  /**
   * Send a report about a message
   */
  async send_report(message_id: string, user: BackendUserCore, text: string) {
    return this.post("/api/v1/text_labels", {
      type: "text_labels",
      message_id,
      labels: [], // Not yet implemented
      text,
      is_report: true,
      user,
    });
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
  async fetch_valid_text(messageId?: string): Promise<any> {
    return this.get("/api/v1/text_labels/valid_labels", { message_id: messageId });
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

  /**
   * Add/remove an emoji on a message for a user
   */
  async set_user_message_emoji(message_id: string, user: BackendUserCore, emoji: string, op: EmojiOp): Promise<void> {
    await this.post(`/api/v1/messages/${message_id}/emoji`, {
      user,
      emoji,
      op,
    });
  }

  fetch_my_messages(user: BackendUserCore) {
    const params = new URLSearchParams({
      username: user.id,
      auth_method: user.auth_method,
    });
    return this.get<Message[]>(`/api/v1/messages?${params}`);
  }

  fetch_recent_messages() {
    return this.get<Message[]>(`/api/v1/messages`);
  }

  fetch_message_children(messageId: string) {
    return this.get<Message[]>(`/api/v1/messages/${messageId}/children`);
  }

  fetch_conversation(messageId: string) {
    return this.get(`/api/v1/messages/${messageId}/conversation`);
  }

  async fetch_tos_acceptance(user: BackendUserCore): Promise<BackendUser["tos_acceptance_date"]> {
    const backendUser = await this.get<BackendUser>(`/api/v1/frontend_users/${user.auth_method}/${user.id}`);
    return backendUser.tos_acceptance_date;
  }

  async set_tos_acceptance(user: BackendUserCore) {
    // NOTE: we do a post here to force create the user if it does not exist
    const backendUser = await this.post<BackendUser>(`/api/v1/frontend_users/`, user);
    await this.put<void>(`/api/v1/users/${backendUser.user_id}?tos_acceptance=true`);
  }
}
