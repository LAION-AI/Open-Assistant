export const taskTypes = {
  create: {
    initial_prompt: {
      endpoint: "initial_prompt",
      label: "Create Initial Prompts",
      desc: "Write initial prompts to help Open Assistant to try replying to diverse messages.",
      header: "Start a conversation",
      instructions: "Create an initial message to send to the assistant",
    },
    user_reply: {
      endpoint: "prompter_reply",
      label: "Reply as User",
      desc: "Chat with Open Assistant and help improve it’s responses as you interact with it.",
      header: "Reply as a user",
      instructions: "Given the following conversation, provide an adequate reply",
    },
    assistant_reply: {
      endpoint: "assistant_reply ",
      label: "Reply as Assistant",
      desc: "Help Open Assistant improve its responses to conversations with other users.",
      header: "Reply as the assistant",
      instructions: "Given the following conversation, provide an adequate reply",
    },
  },
  evaluate: {
    rank_user_replies: {
      endpoint: "rank_prompter_replies",
      label: "Rank User Replies",
      desc: "Help Open Assistant improve its responses to conversations with other users.",
      header: "Instructions",
      instructions: "Given the following replies, sort them from best to worst, best being first, worst being last.",
      sortable: "replies",
    },
    rank_assistant_replies: {
      endpoint: "rank_assistant_replies",
      label: "Rank Assistant Replies",
      desc: "Score prompts given by Open Assistant based on their accuracy and readability.",
      header: "Instructions",
      instructions: "Given the following replies, sort them from best to worst, best being first, worst being last.",
      sortable: "replies",
    },
    rank_initial_prompts: {
      endpoint: "rank_initial_prompts",
      label: "Rank Initial Prompts",
      desc: "Score prompts given by Open Assistant based on their accuracy and readability.",
      header: "Instructions",
      instructions: "Given the following prompts, sort them from best to worst, best being first, worst being last.",
      sortable: "prompts",
    },
  },
};
