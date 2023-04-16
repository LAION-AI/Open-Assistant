import { createContext, PropsWithChildren, useContext, useMemo } from "react";
import { InferenceMessage, ModelInfo } from "src/types/Chat";

export type ChatContext = {
  modelInfos: ModelInfo[];
  messages: InferenceMessage[];
};

const chatContext = createContext<ChatContext>({} as ChatContext);

export const useChatContext = () => useContext(chatContext);

export const ChatContextProvider = ({ children, modelInfos, messages }: PropsWithChildren<ChatContext>) => {
  const value = useMemo(() => ({ modelInfos, messages }), [messages, modelInfos]);

  return <chatContext.Provider value={value}>{children}</chatContext.Provider>;
};
