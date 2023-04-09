import { boolean } from "boolean";

import { getEnv } from "./browserEnv";

export const isChatEnable = () => {
  return boolean(getEnv().ENABLE_CHAT);
};
