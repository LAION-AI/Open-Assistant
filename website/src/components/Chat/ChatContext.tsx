import { createContext, PropsWithChildren, useContext, useMemo } from "react";
import { InferenceMessage, ModelInfo, PluginEntry } from "src/types/Chat";

export type ChatContext = {
  modelInfos: ModelInfo[];
  messages: InferenceMessage[];
  plugins: PluginEntry[];
};

const chatContext = createContext<ChatContext>({} as ChatContext);

export const useChatContext = () => useContext(chatContext);

export const ChatContextProvider = ({ children, modelInfos, messages, plugins }: PropsWithChildren<ChatContext>) => {
  const value = useMemo(() => ({ modelInfos, messages, plugins }), [messages, modelInfos, plugins]);

  return <chatContext.Provider value={value}>{children}</chatContext.Provider>;
};
