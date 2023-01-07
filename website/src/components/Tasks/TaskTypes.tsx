export const TaskTypes = [
  {
    label: "Create Initial Prompts",
    desc: "Write initial prompts to help Open Assistant to try replying to diverse messages.",
    category: "create",
    pathname: "/create/initial_prompt",
    type: "initial_prompt",
  },
  {
    label: "Reply as User",
    desc: "Chat with Open Assistant and help improve it’s responses as you interact with it.",
    category: "create",
    pathname: "/create/user_reply",
    type: "prompter_reply",
  },
  {
    label: "Reply as Assistant",
    desc: "Help Open Assistant improve its responses to conversations with other users.",
    category: "create",
    pathname: "/create/assistant_reply",
    type: "assistant_reply",
  },
  {
    label: "Rank User Replies",
    category: "evaluate",
    desc: "Help Open Assistant improve its responses to conversations with other users.",
    pathname: "/evaluate/rank_user_replies",
    type: "rank_prompter_replies",
  },
  {
    label: "Rank Assistant Replies",
    desc: "Score prompts given by Open Assistant based on their accuracy and readability.",
    category: "evaluate",
    pathname: "/evaluate/rank_assistant_replies",
    type: "rank_assistant_replies",
  },
  {
    label: "Rank Initial Prompts",
    desc: "Score prompts given by Open Assistant based on their accuracy and readability.",
    category: "evaluate",
    pathname: "/evaluate/rank_initial_prompts",
    type: "rank_initial_prompts",
  },
];
