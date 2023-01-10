export enum TaskCategory {
  Tasks = "Tasks",
  Create = "Create",
  Evaluate = "Evaluate",
  Label = "Label",
}

export interface TaskInfo {
  label: string;
  desc: string;
  category: TaskCategory;
  pathname: string;
  type: string;
  overview?: string;
  instruction?: string;
  update_type: string;
  unchanged_title?: string;
  unchanged_message?: string;
}

export const TaskTypes: TaskInfo[] = [
  // general/random
  {
    label: "Grab a task",
    desc: "Help us improve Open Assistant by grabbing a task ...",
    category: TaskCategory.Tasks,
    pathname: "/tasks/random",
    type: "random",
  },
  // create
  {
    label: "Create Initial Prompts",
    desc: "Write initial prompts to help Open Assistant to try replying to diverse messages.",
    category: TaskCategory.Create,
    pathname: "/create/initial_prompt",
    type: "initial_prompt",
    overview: "Create an initial message to send to the assistant",
    instruction: "Provide the initial prompt",
    update_type: "text_reply_to_message",
  },
  {
    label: "Reply as User",
    desc: "Chat with Open Assistant and help improve it’s responses as you interact with it.",
    category: TaskCategory.Create,
    pathname: "/create/user_reply",
    type: "prompter_reply",
    overview: "Given the following conversation, provide an adequate reply",
    instruction: "Provide the user`s reply",
    update_type: "text_reply_to_message",
  },
  {
    label: "Reply as Assistant",
    desc: "Help Open Assistant improve its responses to conversations with other users.",
    category: TaskCategory.Create,
    pathname: "/create/assistant_reply",
    type: "assistant_reply",
    overview: "Given the following conversation, provide an adequate reply",
    instruction: "Provide the assistant`s reply",
    update_type: "text_reply_to_message",
  },
  // evaluate
  {
    label: "Rank User Replies",
    category: TaskCategory.Evaluate,
    desc: "Help Open Assistant improve its responses to conversations with other users.",
    pathname: "/evaluate/rank_user_replies",
    type: "rank_prompter_replies",
    update_type: "message_ranking",
    unchanged_title: "Order Unchanged",
    unchanged_message: "You have not changed the order of the prompts. Are you sure you would like to submit?",
  },
  {
    label: "Rank Assistant Replies",
    desc: "Score prompts given by Open Assistant based on their accuracy and readability.",
    category: TaskCategory.Evaluate,
    pathname: "/evaluate/rank_assistant_replies",
    type: "rank_assistant_replies",
    update_type: "message_ranking",
    unchanged_title: "Order Unchanged",
    unchanged_message: "You have not changed the order of the prompts. Are you sure you would like to submit?",
  },
  {
    label: "Rank Initial Prompts",
    desc: "Score prompts given by Open Assistant based on their accuracy and readability.",
    category: TaskCategory.Evaluate,
    pathname: "/evaluate/rank_initial_prompts",
    type: "rank_initial_prompts",
    update_type: "message_ranking",
    unchanged_title: "Order Unchanged",
    unchanged_message: "You have not changed the order of the prompts. Are you sure you would like to submit?",
  },
  // label
  {
    label: "Label Initial Prompt",
    desc: "Provide labels for a prompt.",
    category: TaskCategory.Label,
    pathname: "/label/label_initial_prompt",
    overview: "Provide labels for the following prompt",
    type: "label_initial_prompt",
    update_type: "text_labels",
  },
  {
    label: "Label Prompter Reply",
    desc: "Provide labels for a prompt.",
    category: TaskCategory.Label,
    pathname: "/label/label_prompter_reply",
    overview: "Given the following discussion, provide labels for the final promp",
    type: "label_prompter_reply",
    update_type: "text_labels",
  },
  {
    label: "Label Assistant Reply",
    desc: "Provide labels for a prompt.",
    category: TaskCategory.Label,
    pathname: "/label/label_assistant_reply",
    overview: "Given the following discussion, provide labels for the final prompt.",
    type: "label_assistant_reply",
    update_type: "text_labels",
  },
];
