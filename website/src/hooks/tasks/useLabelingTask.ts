import { BaseTask, TaskResponse, TaskType } from "src/types/Task";
import { LabelAssistantReplyTask, LabelInitialPromptTask, LabelPrompterReplyTask } from "src/types/Tasks";

import { useGenericTaskAPI } from "./useGenericTaskAPI";

const useLabelingTask = <Task extends BaseTask>(
  endpoint: TaskType.label_assistant_reply | TaskType.label_prompter_reply | TaskType.label_initial_prompt
) => {
  const { tasks, isLoading, trigger, reset, error } = useGenericTaskAPI<Task>(endpoint);

  const submit = (id: string, message_id: string, text: string, validLabels: string[], labelWeights: number[]) => {
    console.assert(validLabels.length === labelWeights.length);
    const labels = Object.fromEntries(validLabels.map((label, i) => [label, labelWeights[i]]));

    return trigger({ id, update_type: "text_labels", content: { labels, text, message_id } });
  };

  return { tasks, isLoading, submit, reset, error };
};

export type LabelAssistantReplyTaskResponse = TaskResponse<LabelAssistantReplyTask>;

export const useLabelAssistantReplyTask = () =>
  useLabelingTask<LabelAssistantReplyTask>(TaskType.label_assistant_reply);

export type LabelInitialPromptTaskResponse = TaskResponse<LabelInitialPromptTask>;

export const useLabelInitialPromptTask = () => useLabelingTask<LabelInitialPromptTask>(TaskType.label_initial_prompt);

export type LabelPrompterReplyTaskResponse = TaskResponse<LabelPrompterReplyTask>;

export const useLabelPrompterReplyTask = () => useLabelingTask<LabelPrompterReplyTask>(TaskType.label_prompter_reply);
