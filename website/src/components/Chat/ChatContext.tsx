import { createContext, PropsWithChildren, useContext, useMemo } from "react";
import { ModelInfo } from "src/types/Chat";

export type ChatContext = {
  modelInfos: ModelInfo[];
};

const chatContext = createContext<ChatContext>({} as ChatContext);

export const useChatContext = () => useContext(chatContext);

export const ChatContextProvider = ({ children, modelInfos }: PropsWithChildren<ChatContext>) => {
  const value = useMemo(() => ({ modelInfos }), [modelInfos]);

  return <chatContext.Provider value={value}>{children}</chatContext.Provider>;
};
