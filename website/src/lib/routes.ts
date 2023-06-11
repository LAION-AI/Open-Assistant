import { CursorPaginationState } from "src/components/DataTable/useCursorPagination";
import { TaskType } from "src/types/Task";

export type RouteQuery = Record<string, string | number | boolean | undefined>;

export const stringifyQuery = (query: RouteQuery | undefined) => {
  if (!query) {
    return "";
  }

  const filteredQuery = Object.fromEntries(Object.entries(query).filter(([, value]) => value !== undefined)) as Record<
    string,
    string
  >;

  return new URLSearchParams(filteredQuery).toString();
};

const createRoute = (path: string, query?: RouteQuery) => {
  if (!query) {
    return path;
  }

  return `${path}?${stringifyQuery(query)}`;
};

export const ROUTES = {
  ADMIN_MESSAGE_DETAIL: (id: string) => `/admin/messages/${id}`,
  MESSAGE_DETAIL: (id: string) => `/messages/${id}`,
  ADMIN_USER_DETAIL: (id: string) => `/admin/manage_user/${id}`,
  CHAT: (id: string) => `/chat/${id}`,
  ADMIN_MESSAGE_EDIT: (id: string) => `/admin/edit/${id}`,
};

export type QueryWithLang<T extends RouteQuery | undefined = undefined> = T extends undefined
  ? { lang: string }
  : T & { lang: string };

const withLang =
  <T extends RouteQuery | undefined = undefined>(path: string, q?: T) =>
  (query: QueryWithLang<T>) => {
    return createRoute(path, { ...q, ...query });
  };

export const API_ROUTES = {
  NEW_TASK: (type: TaskType, query: QueryWithLang) => createRoute(`/api/new_task/${type}`, query),
  UPDATE_TASK: "/api/update_task",
  AVAILABLE_TASK: withLang("/api/available_tasks"),
  RECENT_MESSAGES: withLang("/api/messages"),
  ADMIN_DELETE_MESSAGE: (messageId: string) => createRoute(`/api/admin/delete_message/${messageId}`),
  ADMIN_UNDELETE_MESSAGE: (messageId: string) => createRoute(`/api/admin/undelete_message/${messageId}`),
  ADMIN_EDIT_MESSAGE: (messageId: string) => createRoute(`/api/admin/edit_message/${messageId}`),
  ADMIN_MESSAGE_LIST: (
    query: CursorPaginationState & { user_id?: string; include_user?: boolean; search_query?: string; lang?: string }
  ) => createRoute("/api/admin/messages", query),
  // chat:
  GET_CHAT: (chat_id: string) => createRoute(`/api/chat`, { chat_id }),
  LIST_CHAT: "/api/chat",
  LIST_CHAT_WITH_PARMS: (params: RouteQuery) => createRoute(API_ROUTES.LIST_CHAT, params),
  GET_MESSAGE: (chat_id: string, message_id: string) => createRoute(`/api/chat/message`, { chat_id, message_id }),
  CREATE_PROMPTER_MESSAGE: `/api/chat/prompter_message`,
  CREATE_ASSISTANT_MESSAGE: `/api/chat/assistant_message`,
  CHAT_MESSAGE_VOTE: `/api/chat/vote`,
  CHAT_MESSAGE_EVAL: `/api/chat/message_eval`,
  STREAM_CHAT_MESSAGE: (chat_id: string, message_id: string) =>
    createRoute(`/api/chat/events`, { chat_id, message_id }),
  GET_CHAT_MODELS: "/api/chat/models",
  UPDATE_CHAT: () => `/api/chat`,
  GET_PLUGIN_CONFIG: `/api/chat/plugin_config`,
  DELETE_CHAT: (chat_id: string) => createRoute(`/api/chat`, { chat_id }),
};
