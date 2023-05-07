import { createContext, PropsWithChildren, useContext, useMemo } from "react";
import { ModelInfo, PluginEntry } from "src/types/Chat";

export type ChatInitialDataContext = {
  modelInfos: ModelInfo[];
  builtInPlugins: PluginEntry[];
};

const chatInitialDataContext = createContext<ChatInitialDataContext>({} as ChatInitialDataContext);

export const useChatInitialData = () => useContext(chatInitialDataContext);

export const ChatInitialDataProvider = ({
  children,
  modelInfos,
  builtInPlugins,
}: PropsWithChildren<ChatInitialDataContext>) => {
  const value = useMemo(() => ({ modelInfos, builtInPlugins }), [modelInfos, builtInPlugins]);

  return <chatInitialDataContext.Provider value={value}>{children}</chatInitialDataContext.Provider>;
};
