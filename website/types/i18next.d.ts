import type common from "public/locales/en/common.json";
import type dashboard from "public/locales/en/dashboard.json";
import type error from "public/locales/en/error.json";
import type index from "public/locales/en/index.json";
import type labelling from "public/locales/en/labelling.json";
import type leaderboard from "public/locales/en/leaderboard.json";
import type message from "public/locales/en/message.json";
import type stats from "public/locales/en/stats.json";
import type tasks from "public/locales/en/tasks.json";
import type tos from "public/locales/en/tos.json";
declare module "i18next" {
  interface CustomTypeOptions {
    resources: {
      common: typeof common;
      dashboard: typeof dashboard;
      error: typeof error;
      index: typeof index;
      labelling: typeof labelling;
      leaderboard: typeof leaderboard;
      message: typeof message;
      stats: typeof stats;
      tasks: typeof tasks;
      tos: typeof tos;
    };
  }
}
