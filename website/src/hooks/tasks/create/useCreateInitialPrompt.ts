import { useGenericTaskAPI } from "../useGenericTaskAPI";

interface CreateInitialPromptTask {
  id: string;
  type: "initial_prompt";
  hint: string;
}

export const useCreateInitialPrompt = () => useGenericTaskAPI<CreateInitialPromptTask>("initial_prompt");
