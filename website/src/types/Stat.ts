export type HumanMessagesByLang = {
  [key: string]: number;
};

export type HumanMessagesByRole = {
  prompter: number;
  assistant: number;
};

export type MessageTreesByState = {
  state: string;
  count: number;
}[];

export type MessageTreesStatesByLang = {
  lang: string;
  count: number;
  state: string;
}[];

export type UserAcceptesdTos = {
  count: number;
};

export type Stat = {
  name: string;
  last_updated: string;
  stats: HumanMessagesByLang | HumanMessagesByRole | MessageTreesByState | MessageTreesStatesByLang | UserAcceptesdTos;
};

export type Stats = {
  stats_by_name: {
    human_messages_by_lang: Stat & {
      stats: HumanMessagesByLang;
    };
    human_messages_by_role: Stat & {
      stats: HumanMessagesByRole;
    };
    message_trees_by_state: Stat & {
      stats: MessageTreesByState;
    };
    message_trees_states_by_lang: Stat & {
      stats: MessageTreesStatesByLang;
    };
    users_accepted_tos: Stat & {
      stats: UserAcceptesdTos;
    };
  };
};

export type StatNames = keyof Stats["stats_by_name"];
