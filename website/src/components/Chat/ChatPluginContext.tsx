import { createContext, Dispatch, ReactNode, SetStateAction, useContext, useMemo, useState } from "react";
import { PluginEntry } from "src/types/Chat";

export type IChatPluginContext = {
  plugins: PluginEntry[];
  setPlugins: Dispatch<SetStateAction<PluginEntry[]>>;
};

const ChatPluginContext = createContext({} as IChatPluginContext);

export const useChatPluginContext = () => {
  return useContext(ChatPluginContext);
};

export const ChatPluginContextProvider = ({ children }: { children: ReactNode }) => {
  const [plugins, setPlugins] = useState<PluginEntry[]>([]);

  const value = useMemo(() => {
    return { plugins, setPlugins };
  }, [plugins]);

  return <ChatPluginContext.Provider value={value}>{children}</ChatPluginContext.Provider>;
};
