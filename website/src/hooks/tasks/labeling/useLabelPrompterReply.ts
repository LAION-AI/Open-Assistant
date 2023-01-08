import { TaskResponse } from "../useGenericTaskAPI";
import { LabelingTaskType, useLabelingTask } from "./useLabelingTask";

export interface LabelPrompterReplyTask {
  id: string;
  type: LabelingTaskType.label_prompter_reply;
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

export type LabelPrompterReplyTaskResponse = TaskResponse<LabelPrompterReplyTask>;

export const useLabelPrompterReplyTask = () =>
  useLabelingTask<LabelPrompterReplyTask>(LabelingTaskType.label_prompter_reply);
