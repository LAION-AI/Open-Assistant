import pino, { multistream } from "pino";
const isDev = process.env.NODE_ENV === "development";

const streams = [{ stream: process.stdout }];

// this should be imported from server side code only
export const logger = pino(
  {
    level: isDev ? "debug" : "info",
    transport: isDev
      ? {
          target: "pino-pretty",
          options: {
            colorize: true,
          },
        }
      : undefined,
  },
  multistream(streams)
);
