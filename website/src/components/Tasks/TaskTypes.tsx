export enum TaskCategory {
  Create = "Create",
  Evaluate = "Evaluate",
  Label = "Label",
}

export interface TaskType {
  label: string;
  desc: string;
  category: TaskCategory;
  pathname: string;
  type: string;
  overview?: string;
  instruction?: string;
}

export const TaskTypes: TaskType[] = [
  // create
  {
    label: "Create Initial Prompts",
    desc: "Write initial prompts to help Open Assistant to try replying to diverse messages.",
    category: TaskCategory.Create,
    pathname: "/create/initial_prompt",
    type: "initial_prompt",
    overview: "Create an initial message to send to the assistant",
    instruction: "Provide the initial prompt",
  },
  {
    label: "Reply as User",
    desc: "Chat with Open Assistant and help improve it’s responses as you interact with it.",
    category: TaskCategory.Create,
    pathname: "/create/user_reply",
    type: "prompter_reply",
    overview: "Given the following conversation, provide an adequate reply",
    instruction: "Provide the user`s reply",
  },
  {
    label: "Reply as Assistant",
    desc: "Help Open Assistant improve its responses to conversations with other users.",
    category: TaskCategory.Create,
    pathname: "/create/assistant_reply",
    type: "assistant_reply",
    overview: "Given the following conversation, provide an adequate reply",
    instruction: "Provide the assistant`s reply",
  },
  // evaluate
  {
    label: "Rank User Replies",
    category: TaskCategory.Evaluate,
    desc: "Help Open Assistant improve its responses to conversations with other users.",
    pathname: "/evaluate/rank_user_replies",
    type: "rank_prompter_replies",
  },
  {
    label: "Rank Assistant Replies",
    desc: "Score prompts given by Open Assistant based on their accuracy and readability.",
    category: TaskCategory.Evaluate,
    pathname: "/evaluate/rank_assistant_replies",
    type: "rank_assistant_replies",
  },
  {
    label: "Rank Initial Prompts",
    desc: "Score prompts given by Open Assistant based on their accuracy and readability.",
    category: TaskCategory.Evaluate,
    pathname: "/evaluate/rank_initial_prompts",
    type: "rank_initial_prompts",
  },
  // label
  {
    label: "Label Initial Prompt",
    desc: "Provide labels for a prompt.",
    category: TaskCategory.Label,
    pathname: "/label/label_initial_prompt",
    type: "label_initial_prompt",
  },
  {
    label: "Label Prompter Reply",
    desc: "Provide labels for a prompt.",
    category: TaskCategory.Label,
    pathname: "/label/label_prompter_reply",
    type: "label_prompter_reply",
  },
  {
    label: "Label Assistant Reply",
    desc: "Provide labels for a prompt.",
    category: TaskCategory.Label,
    pathname: "/label/label_assistant_reply",
    type: "label_assistant_reply",
  },
];
