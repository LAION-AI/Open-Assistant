import { boolean } from "boolean";

export const isChatEnabled = () => {
  return process.env.NODE_ENV === "development" || boolean(process.env.ENABLE_CHAT);
};
