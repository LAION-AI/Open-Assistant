import "i18next";

import type common from "../public/locales/en/common.json";
import type index from "../public/locales/en/index.json";
import type leaderboard from "../public/locales/en/leaderboard.json";

declare module "i18next" {
  interface CustomTypeOptions {
    resources: {
      common: typeof common;
      index: typeof index;
      leaderboard: typeof leaderboard;
    };
  }
}
