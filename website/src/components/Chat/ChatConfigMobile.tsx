import { Drawer, DrawerBody, DrawerCloseButton, DrawerContent, DrawerHeader, DrawerOverlay } from "@chakra-ui/react";
import { Settings } from "lucide-react";
import { useTranslation } from "next-i18next";
import { memo, ReactNode } from "react";
import SimpleBar from "simplebar-react";

import { useChatActions, useChatState } from "./ChatContext";
import { ChatInputIconButton } from "./ChatInputIconButton";

export const ChatConfigMobile = memo(function ChatConfigDrawer({ children }: { children: ReactNode }) {
  const { t } = useTranslation("chat");

  const { closeConfigDrawer } = useChatActions();
  const { isConfigDrawerOpen } = useChatState();
  return (
    <>
      <Drawer placement="right" onClose={closeConfigDrawer} isOpen={isConfigDrawerOpen}>
        <DrawerOverlay />
        <DrawerContent>
          <DrawerCloseButton />
          <DrawerHeader borderBottomWidth="1px">{t("config_title")}</DrawerHeader>
          <DrawerBody pr="0">
            <SimpleBar
              style={{ maxHeight: "100%", height: "100%", minHeight: "0" }}
              classNames={{
                contentEl: "mr-4 flex flex-col overflow-y-auto items-center",
              }}
            >
              {children}
            </SimpleBar>
          </DrawerBody>
        </DrawerContent>
      </Drawer>
    </>
  );
});

export const ChatConfigMobileTrigger = () => {
  const { t } = useTranslation("chat");
  const { openConfigDrawer } = useChatActions();

  return (
    <ChatInputIconButton
      aria-label={t("config_title")}
      icon={Settings}
      onClick={openConfigDrawer}
      borderRadius="xl"
      display={{ base: "flex", xl: "none" }}
    />
  );
};
