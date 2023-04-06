import { boolean } from "boolean";

// only works server side
export const isSSRChatEnabled = () => {
  return process.env.NODE_ENV === "development" || boolean(process.env.ENABLE_CHAT);
};
