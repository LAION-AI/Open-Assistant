export enum TaskCategory {
  Create = "Create",
  Evaluate = "Evaluate",
  Label = "Label",
  Random = "Random",
}

export enum TaskUpdateType {
  MessageRanking = "message_ranking",
  Random = "random",
  TextLabels = "text_labels",
  TextReplyToMessage = "text_reply_to_message",
}

export enum TaskType {
  AssistantReply = "assistant_reply",
  InitialPrompt = "initial_prompt",
  LabelAssistantReply = "label_assistant_reply",
  LabelInitialPrompt = "label_initial_prompt",
  LabelPrompterReply = "label_prompter_reply",
  PrompterReply = "prompter_reply",
  Random = "random",
  RankAssistantReplies = "rank_assistant_replies",
  RankInitialPrompts = "rank_initial_prompts",
  RankPrompterReplies = "rank_prompter_replies",
}

export interface TaskInfo {
  category: TaskCategory;
  help_link: string;
  id: string;
  mode?: string;
  pathname: string;
  type: string;
  update_type: string;
}

export const TaskCategoryLabels: { [key in TaskCategory]: string } = {
  [TaskCategory.Random]: "grab_a_task",
  [TaskCategory.Create]: "create",
  [TaskCategory.Evaluate]: "evaluate",
  [TaskCategory.Label]: "label",
};

export const TaskInfos: TaskInfo[] = [
  // general/random
  {
    id: "random",
    category: TaskCategory.Random,
    pathname: "/tasks/random",
    help_link: "https://projects.laion.ai/Open-Assistant/docs/guides/prompting",
    type: TaskType.Random,
    update_type: TaskUpdateType.Random,
  },
  // create
  {
    id: "create_initial_prompt",
    category: TaskCategory.Create,
    pathname: "/create/initial_prompt",
    help_link: "https://projects.laion.ai/Open-Assistant/docs/guides/prompting",
    type: TaskType.InitialPrompt,
    update_type: TaskUpdateType.TextReplyToMessage,
  },
  {
    id: "reply_as_user",
    category: TaskCategory.Create,
    pathname: "/create/user_reply",
    help_link: "https://projects.laion.ai/Open-Assistant/docs/tasks/reply_as_user",
    type: TaskType.PrompterReply,
    update_type: TaskUpdateType.TextReplyToMessage,
  },
  {
    id: "reply_as_assistant",
    category: TaskCategory.Create,
    pathname: "/create/assistant_reply",
    help_link: "https://projects.laion.ai/Open-Assistant/docs/tasks/reply_as_assistant",
    type: TaskType.AssistantReply,
    update_type: TaskUpdateType.TextReplyToMessage,
  },
  // evaluate
  {
    id: "rank_user_replies",
    category: TaskCategory.Evaluate,
    pathname: "/evaluate/rank_user_replies",
    help_link: "https://projects.laion.ai/Open-Assistant/docs/guides/prompting",
    type: TaskType.RankPrompterReplies,
    update_type: TaskUpdateType.MessageRanking,
  },
  {
    id: "rank_assistant_replies",
    category: TaskCategory.Evaluate,
    pathname: "/evaluate/rank_assistant_replies",
    help_link: "https://projects.laion.ai/Open-Assistant/docs/guides/prompting",
    type: TaskType.RankAssistantReplies,
    update_type: TaskUpdateType.MessageRanking,
  },
  {
    id: "rank_initial_prompts",
    category: TaskCategory.Evaluate,
    pathname: "/evaluate/rank_initial_prompts",
    help_link: "https://projects.laion.ai/Open-Assistant/docs/guides/prompting",
    type: TaskType.RankInitialPrompts,
    update_type: TaskUpdateType.MessageRanking,
  },
  // label (full)
  {
    id: "label_initial_prompt",
    category: TaskCategory.Label,
    pathname: "/label/label_initial_prompt",
    help_link: "https://projects.laion.ai/Open-Assistant/docs/guides/prompting",
    type: TaskType.LabelInitialPrompt,
    mode: "full",
    update_type: TaskUpdateType.TextLabels,
  },
  {
    id: "label_prompter_reply",
    category: TaskCategory.Label,
    pathname: "/label/label_prompter_reply",
    help_link: "https://projects.laion.ai/Open-Assistant/docs/tasks/label_prompter_reply",
    type: TaskType.LabelPrompterReply,
    mode: "full",
    update_type: TaskUpdateType.TextLabels,
  },
  {
    id: "label_assistant_reply",
    category: TaskCategory.Label,
    pathname: "/label/label_assistant_reply",
    help_link: "https://projects.laion.ai/Open-Assistant/docs/tasks/label_assistant_reply",
    type: TaskType.LabelAssistantReply,
    mode: "full",
    update_type: TaskUpdateType.TextLabels,
  },
  // label (simple)
  {
    id: "classify_initial_prompt",
    category: TaskCategory.Label,
    pathname: "/label/label_initial_prompt",
    help_link: "https://projects.laion.ai/Open-Assistant/docs/guides/prompting",
    type: TaskType.LabelInitialPrompt,
    mode: "simple",
    update_type: TaskUpdateType.TextLabels,
  },
  {
    id: "classify_prompter_reply",
    category: TaskCategory.Label,
    pathname: "/label/label_prompter_reply",
    help_link: "https://projects.laion.ai/Open-Assistant/docs/guides/prompting",
    type: TaskType.LabelPrompterReply,
    mode: "simple",
    update_type: TaskUpdateType.TextLabels,
  },
  {
    id: "classify_assistant_reply",
    category: TaskCategory.Label,
    pathname: "/label/label_assistant_reply",
    help_link: "https://projects.laion.ai/Open-Assistant/docs/guides/prompting",
    type: TaskType.LabelAssistantReply,
    mode: "simple",
    update_type: TaskUpdateType.TextLabels,
  },
];
