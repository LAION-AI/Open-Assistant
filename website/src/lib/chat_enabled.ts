import { boolean } from "boolean";

// only works server side
export const isSSRChatEnabled = () => {
  return boolean(process.env.ENABLE_CHAT);
};
