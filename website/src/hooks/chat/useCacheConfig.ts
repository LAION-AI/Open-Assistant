import { useEffect } from "react";
import { UseFormReturn } from "react-hook-form";
import { ChatConfigForm } from "src/types/Chat";

const CHAT_CONFIG_KEY = "CHAT_CONFIG";

export const getCachedChatForm = (): ChatConfigForm | null => {
  if (typeof localStorage !== "undefined") {
    const oldConfig = localStorage.getItem(CHAT_CONFIG_KEY);
    if (oldConfig) {
      return JSON.parse(oldConfig);
    }
  }
  return null;
};

export const useCacheChatForm = (form: UseFormReturn<ChatConfigForm>) => {
  const config = form.watch();

  useEffect(() => {
    if (typeof localStorage !== "undefined") {
      localStorage.setItem(CHAT_CONFIG_KEY, JSON.stringify(config));
    }
  }, [config]);
};
