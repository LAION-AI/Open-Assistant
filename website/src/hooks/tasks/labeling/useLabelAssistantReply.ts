import { TaskResponse } from "../useGenericTaskAPI";
import { LabelingTaskType, useLabelingTask } from "./useLabelingTask";

export interface LabelAssistantReplyTask {
  id: string;
  type: LabelingTaskType.label_assistant_reply;
  message_id: string;
  valid_labels: string[];
  reply: string;
  conversation: {
    messages: Array<{
      text: string;
      is_assistant: boolean;
      message_id: string;
    }>;
  };
}

export type LabelAssistantReplyTaskResponse = TaskResponse<LabelAssistantReplyTask>;

export const useLabelAssistantReplyTask = () =>
  useLabelingTask<LabelAssistantReplyTask>(LabelingTaskType.label_assistant_reply);
