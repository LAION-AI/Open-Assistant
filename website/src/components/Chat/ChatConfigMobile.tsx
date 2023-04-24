import {
  Drawer,
  DrawerBody,
  DrawerCloseButton,
  DrawerContent,
  DrawerHeader,
  DrawerOverlay,
  useDisclosure,
} from "@chakra-ui/react";
import { Settings } from "lucide-react";
import { useTranslation } from "next-i18next";
import { memo } from "react";

import { ChatConfigForm } from "./ChatConfigForm";
import { ChatInputIconButton } from "./ChatInputIconButton";

export const ChatConfigDrawer = memo(function ChatConfigDrawer() {
  const { isOpen, onOpen, onClose } = useDisclosure();

  const { t } = useTranslation("chat");
  return (
    <>
      <ChatInputIconButton
        aria-label={t("config_title")}
        icon={Settings}
        onClick={onOpen}
        borderRadius="xl"
        display={{ base: "flex", xl: "none" }}
      />
      <Drawer placement="right" onClose={onClose} isOpen={isOpen}>
        <DrawerOverlay />
        <DrawerContent>
          <DrawerCloseButton />
          <DrawerHeader borderBottomWidth="1px">{t("config_title")}</DrawerHeader>
          <DrawerBody>
            <ChatConfigForm />
          </DrawerBody>
        </DrawerContent>
      </Drawer>
    </>
  );
});
