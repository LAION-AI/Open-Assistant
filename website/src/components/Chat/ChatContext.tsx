import { createContext, PropsWithChildren, useContext, useMemo } from "react";
import { ModelInfo, PluginEntry } from "src/types/Chat";

export type ChatContext = {
  modelInfos: ModelInfo[];
  plugins: PluginEntry[];
};

const chatContext = createContext<ChatContext>({} as ChatContext);

export const useChatContext = () => useContext(chatContext);

export const ChatContextProvider = ({ children, modelInfos, plugins }: PropsWithChildren<ChatContext>) => {
  const value = useMemo(() => ({ modelInfos, plugins }), [modelInfos, plugins]);

  return <chatContext.Provider value={value}>{children}</chatContext.Provider>;
};
