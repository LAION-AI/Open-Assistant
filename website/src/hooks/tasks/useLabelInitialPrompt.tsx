import { TaskResponse, useGenericTaskAPI } from "./useGenericTaskAPI";

export interface LabelInitialPromptTask {
  id: string;
  type: "label_initial_prompt";
  message_id: string;
  valid_labels: string[];
  prompt: string;
}

export type LabelInitialPromptTaskResponse = TaskResponse<LabelInitialPromptTask>;

export const useLabelInitialPromptTask = () => {
  const { tasks, isLoading, trigger, reset, error } = useGenericTaskAPI<LabelInitialPromptTask>("label_initial_prompt");

  const submit = (id: string, message_id: string, text: string, validLabels: string[], labelWeights: number[]) => {
    console.assert(validLabels.length === labelWeights.length);
    const labels = Object.fromEntries(validLabels.map((label, i) => [label, labelWeights[i]]));

    return trigger({ id, update_type: "text_labels", content: { labels, text, message_id } });
  };

  return { tasks, isLoading, submit, reset, error };
};
