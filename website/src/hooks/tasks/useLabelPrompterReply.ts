import { TaskResponse, useGenericTaskAPI } from "./useGenericTaskAPI";

export interface LabelPrompterReplyTask {
  id: string;
  type: "label_prompter_reply";
  message_id: string;
  valid_labels: string[];
  reply: string;
  conversation: {
    messages: Array<{
      text: string;
      is_assistant: boolean;
    }>;
  };
}

export type LabelPrompterReplyTaskResponse = TaskResponse<LabelPrompterReplyTask>;

export const useLabelPrompterReplyTask = () => {
  const { tasks, isLoading, trigger, reset, error } = useGenericTaskAPI<LabelPrompterReplyTask>("label_prompter_reply");

  const submit = (id: string, message_id: string, text: string, validLabels: string[], labelWeights: number[]) => {
    console.assert(validLabels.length === labelWeights.length);
    const labels = Object.fromEntries(validLabels.map((label, i) => [label, labelWeights[i]]));

    return trigger({ id, update_type: "text_labels", content: { labels, text, message_id } });
  };

  return { tasks, isLoading, submit, reset, error };
};
