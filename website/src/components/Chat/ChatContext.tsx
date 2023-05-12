import { useDisclosure } from "@chakra-ui/react";
import { createContext, ReactNode, useContext, useMemo } from "react";

export type ChatStateContext = {
  isConfigDrawerOpen: boolean;
};

export type ChatActionContext = {
  openConfigDrawer: () => void;
  closeConfigDrawer: () => void;
};

const chatStateContext = createContext<ChatStateContext>({} as ChatStateContext);
const chatActionContext = createContext<ChatActionContext>({} as ChatActionContext);

export const useChatState = () => useContext(chatStateContext);

export const useChatActions = () => useContext(chatActionContext);

export const ChatProvider = ({ children }: { children: ReactNode }) => {
  const { isOpen, onOpen, onClose } = useDisclosure();
  const state: ChatStateContext = useMemo(() => ({ isConfigDrawerOpen: isOpen }), [isOpen]);
  const action: ChatActionContext = useMemo(
    () => ({ openConfigDrawer: onOpen, closeConfigDrawer: onClose }),
    [onClose, onOpen]
  );

  return (
    <chatStateContext.Provider value={state}>
      <chatActionContext.Provider value={action}>{children}</chatActionContext.Provider>
    </chatStateContext.Provider>
  );
};
