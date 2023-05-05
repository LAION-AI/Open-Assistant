import { createContext, PropsWithChildren, useContext, useMemo } from "react";
import { ModelInfo, PluginEntry } from "src/types/Chat";

export type ChatContext = {
  modelInfos: ModelInfo[];
  builtInPlugins: PluginEntry[];
};

const chatContext = createContext<ChatContext>({} as ChatContext);

export const useChatContext = () => useContext(chatContext);

export const ChatContextProvider = ({ children, modelInfos, builtInPlugins }: PropsWithChildren<ChatContext>) => {
  const value = useMemo(() => ({ modelInfos, builtInPlugins }), [modelInfos, builtInPlugins]);

  return <chatContext.Provider value={value}>{children}</chatContext.Provider>;
};
