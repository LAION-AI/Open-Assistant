import { ChatConfigFormData } from "src/types/Chat";

const CHAT_CONFIG_KEY = "CHAT_CONFIG";

export const setConfigCache = (config: ChatConfigFormData) => {
  if (typeof localStorage !== "undefined") {
    localStorage.setItem(CHAT_CONFIG_KEY, JSON.stringify(config));
  }
};

export const getConfigCache = (): ChatConfigFormData | null => {
  if (typeof localStorage !== "undefined") {
    const oldConfig = localStorage.getItem(CHAT_CONFIG_KEY);
    if (oldConfig) {
      return JSON.parse(oldConfig);
    }
  }
  return null;
};
