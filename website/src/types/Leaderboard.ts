export interface LeaderboardEntry {
  display_name: string;
  ranking: number;
  score: number;
}

export enum LeaderboardTimeFrame {
  day = "day",
  week = "week",
  month = "month",
  total = "total",
}
export interface LeaderboardReply {
  time_frame: LeaderboardTimeFrame;
  last_updated: string; // date time iso string
  leaderboard: LeaderboardEntity[];
}

export interface LeaderboardEntity {
  rank: number;
  user_id: string;
  username: string;
  auth_method: string;
  display_name: string;
  leader_score: number;
  base_date: string;
  image?: string;
  modified_date: string;
  prompts: number;
  replies_assistant: number;
  replies_prompter: number;
  labels_simple: number;
  labels_full: number;
  rankings_total: number;
  rankings_good: number;
  accepted_prompts: number;
  accepted_replies_assistant: number;
  accepted_replies_prompter: number;
  reply_ranked_1: number;
  reply_ranked_2: number;
  reply_ranked_3: number;
  streak_last_day_date: number | null;
  streak_days: number | null;
  highlighted: boolean;
}
