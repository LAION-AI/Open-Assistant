// jest.setup.js
import "@testing-library/jest-dom/extend-expect";

const CONSOLE_FAIL_TYPES = ["error", "warn"];

// Throw errors when a `console.error` or `console.warn` happens
// by overriding the functions.
// If the warning/error is intentional, then catch it and expect for it, like:
//
//  jest.spyOn(console, 'warn').mockImplementation();
//  ...
//  expect(console.warn).toHaveBeenCalledWith(expect.stringContaining('Empty titles are deprecated.'));
CONSOLE_FAIL_TYPES.forEach((type) => {
  const orig_f = console[type];
  console[type] = (...message) => {
    orig_f(...message);
    throw new Error(`Failing due to console.${type} while running test!\n\n${message.join(" ")}`);
  };
});

// use the actual localization values for testing:
import i18n from "i18next";
import common from "public/locales/en/common.json";
import dashboard from "public/locales/en/dashboard.json";
import error from "public/locales/en/error.json";
import index from "public/locales/en/index.json";
import labelling from "public/locales/en/labelling.json";
import leaderboard from "public/locales/en/leaderboard.json";
import message from "public/locales/en/message.json";
import stats from "public/locales/en/stats.json";
import tasks from "public/locales/en/tasks.json";
import tos from "public/locales/en/tos.json";
import { initReactI18next } from "react-i18next";

i18n.use(initReactI18next).init({
  lng: "en",
  fallbackLng: "en",
  resources: {
    en: { common, dashboard, error, index, labelling, leaderboard, message, stats, tasks, tos },
  },
});
