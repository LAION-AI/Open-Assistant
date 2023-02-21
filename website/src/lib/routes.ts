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
};

export type QueryWithLang<T extends RouteQuery | undefined = undefined> = T extends undefined
  ? { lang: string }
  : T & { lang: string };

const withLang =
  <T extends RouteQuery>(path: string, q?: T) =>
  (query?: QueryWithLang<T>) => {
    return createRoute(path, { ...q, ...query });
  };

export const API_ROUTES = {
  NEW_TASK: (type: TaskType, query: QueryWithLang) => createRoute(`/api/new_task/${type}`, query),
  UPDATE_TASK: "/api/update_task",
  AVAILABLE_TASK: withLang("/api/available_tasks"),
  RECENT_MESSAGES: withLang("/api/messages"),
};
