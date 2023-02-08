export enum TrollboardTimeFrame {
  day = "day",
  week = "week",
  month = "month",
  total = "total",
}

export type FetchTrollBoardResponse = {
  time_frame: TrollboardTimeFrame;
  last_updated: string;
  trollboard: TrollboardEntity[];
};

export type TrollboardEntity = {
  rank: number;
  user_id: string;
  highlighted: boolean;
  username: string;
  auth_method: string;
  display_name: string;
  last_activity_date: string | null;
  troll_score: number;
  base_date: string;
  modified_date: string;
  red_flags: number;
  upvotes: number;
  downvotes: number;
  spam_prompts: 0;
  quality: number | null;
  humor: number | null;
  toxicity: number | null;
  violence: number | null;
  helpfulness: number | null;
  spam: number;
  lang_mismach: number;
  not_appropriate: number;
  pii: number;
  hate_speech: number;
  sexual_content: number;
  political_content: number;
};
