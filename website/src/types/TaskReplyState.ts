export interface TaskReplyValid<T> {
  content: T;
  state: "VALID";
}
export interface TaskReplyDefault<T> {
  content: T;
  state: "DEFAULT";
}
export interface TaskReplyInValid<T> {
  content: T;
  state: "INVALID";
}

export type TaskReplyState<T> = TaskReplyValid<T> | TaskReplyDefault<T> | TaskReplyInValid<T>;
