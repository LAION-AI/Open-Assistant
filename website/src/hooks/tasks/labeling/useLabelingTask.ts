import { useGenericTaskAPI } from "../useGenericTaskAPI";

export const enum LabelingTaskType {
  label_initial_prompt = "label_initial_prompt",
  label_prompter_reply = "label_prompter_reply",
  label_assistant_reply = "label_assistant_reply",
}

export const useLabelingTask = <TaskType>(endpoint: LabelingTaskType) => {
  const { tasks, isLoading, trigger, reset, error } = useGenericTaskAPI<TaskType>(endpoint);

  const submit = (id: string, message_id: string, text: string, validLabels: string[], labelWeights: number[]) => {
    console.assert(validLabels.length === labelWeights.length);
    const labels = Object.fromEntries(validLabels.map((label, i) => [label, labelWeights[i]]));

    return trigger({ id, update_type: "text_labels", content: { labels, text, message_id } });
  };

  return { tasks, isLoading, submit, reset, error };
};
