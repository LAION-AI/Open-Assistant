import "i18next";

import type common from "public/locales/en/common.json";
import type dashboard from "public/locales/en/dashboard.json";
import type index from "public/locales/en/index.json";
import type leaderboard from "public/locales/en/leaderboard.json";
import type tasks from "public/locales/en/tasks.json";

declare module "i18next" {
  interface CustomTypeOptions {
    resources: {
      common: typeof common;
      dashboard: typeof dashboard;
      index: typeof index;
      leaderboard: typeof leaderboard;
      tasks: typeof tasks;
    };
  }
}
