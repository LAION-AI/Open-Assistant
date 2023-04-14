import { Drawer, DrawerCloseButton, DrawerContent, DrawerOverlay, IconButton, useDisclosure } from "@chakra-ui/react";
import { AlignJustify } from "lucide-react";
import { useRouter } from "next/router";
import { useTranslation } from "next-i18next";
import { useEffect } from "react";

import { ChatListBase } from "./ChatListBase";

export function ChatListMobile() {
  const { isOpen, onOpen, onClose } = useDisclosure();
  const { t } = useTranslation("chat");
  const { events } = useRouter();

  useEffect(() => {
    const handleRouteChange = () => {
      // close the drawer when the route changes, because drawer not automatically closes when route changes
      onClose();
    };

    events.on("routeChangeStart", handleRouteChange);

    return () => {
      events.off("routeChangeStart", handleRouteChange);
    };
  }, [onClose, events]);

  return (
    <>
      <IconButton
        display={{ base: "flex", md: "none" }}
        onClick={onOpen}
        icon={<AlignJustify />}
        aria-label={t("your_chats")}
        variant="ghost"
        size="md"
        borderRadius="lg"
        m="0"
      ></IconButton>
      <Drawer isOpen={isOpen} placement="left" onClose={onClose}>
        <DrawerOverlay />
        <DrawerContent maxW="260px">
          <DrawerCloseButton
            style={{
              insetInlineEnd: `-2.5rem`,
            }}
            top="29px"
            _dark={{ bg: "gray.600" }}
            bg="white"
          />
          <ChatListBase isSideBar position="relative" h="100vh" />
        </DrawerContent>
      </Drawer>
    </>
  );
}
