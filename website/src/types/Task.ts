export enum TaskType {
  initial_prompt = "initial_prompt",
  assistant_reply = "assistant_reply",
  prompter_reply = "prompter_reply",

  rank_initial_prompts = "rank_initial_prompts",
  rank_assistant_replies = "rank_assistant_replies",
  rank_prompter_replies = "rank_prompter_replies",

  label_initial_prompt = "label_initial_prompt",
  label_prompter_reply = "label_prompter_reply",
  label_assistant_reply = "label_assistant_reply",

  random = "random",
}

export enum TaskCategory {
  Create = "Create",
  Evaluate = "Evaluate",
  Label = "Label",
  Random = "Random",
}

export interface TaskInfo {
  category: TaskCategory;
  help_link: string;
  id: string;
  mode?: string;
  pathname: string;
  type: TaskType;
  update_type: TaskUpdateType;
}

export enum TaskUpdateType {
  MessageRanking = "message_ranking",
  Random = "random",
  TextLabels = "text_labels",
  TextReplyToMessage = "text_reply_to_message",
}

// we need to reconsider how to handle task content types
// eslint-disable-next-line  @typescript-eslint/no-explicit-any
export type TaskContent = any;

export interface ValidLabel {
  name: string;
  display_text: string;
  help_text: string;
}

export interface BaseTask {
  id: string;
  type: TaskType;
}

export interface ServerTaskResponse<Task extends BaseTask> {
  id: string;
  userId: string;
  task: Task;
}

interface TaskAvailable<Task extends BaseTask> extends ServerTaskResponse<Task> {
  taskAvailability: "AVAILABLE";
  taskInfo: TaskInfo;
}

interface AwaitingInitialTask {
  taskAvailability: "AWAITING_INITIAL";
}

interface NoTaskAvailable {
  taskAvailability: "NONE_AVAILABLE";
}

export type TaskResponse<Task extends BaseTask> = TaskAvailable<Task> | AwaitingInitialTask | NoTaskAvailable;

export type TaskReplyValidity = "DEFAULT" | "VALID" | "INVALID";

export type AvailableTasks = { [taskType in TaskType]: number };
