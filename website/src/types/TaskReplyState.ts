export interface TaskReplyValid<T> {
  content: T;
  state: "VALID";
}
export interface TaskReplyDefault<T> {
  content: T;
  state: "DEFAULT";
}

export type TaskReplyState<T> = TaskReplyValid<T> | TaskReplyDefault<T>;
