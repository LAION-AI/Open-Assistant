export interface CreateTaskReply {
  text: string;
}

export interface EvaluateTaskReply {
  ranking: number[];
  not_rankable: boolean;
}

export interface LabelTaskReply {
  text: string;
  labels: Record<string, number>;
  message_id: string;
}

export type AllTaskReplies = CreateTaskReply | EvaluateTaskReply | LabelTaskReply;
