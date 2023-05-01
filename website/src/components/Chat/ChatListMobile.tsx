import {
  Drawer,
  DrawerCloseButton,
  DrawerContent,
  DrawerOverlay,
  Flex,
  IconButton,
  useDisclosure,
} from "@chakra-ui/react";
import { AlignJustify } from "lucide-react";
import { useRouter } from "next/router";
import { useTranslation } from "next-i18next";
import { memo, useEffect } from "react";
import { useSidebarItems } from "src/hooks/layout/sidebarItems";

import { SideMenuItem } from "../SideMenu";
import { ChatListBase } from "./ChatListBase";

export const ChatListMobile = memo(function ChatListMobile() {
  const { isOpen, onOpen, onClose } = useDisclosure();
  const { t } = useTranslation("chat");
  const { events } = useRouter();
  const items = useSidebarItems();

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
        display={{ base: "flex", lg: "none" }}
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
        <DrawerContent>
          <DrawerCloseButton
            style={{
              insetInlineEnd: `-2.5rem`,
            }}
            top="29px"
            _dark={{ bg: "gray.600" }}
            bg="white"
          />
          <div className="flex min-h-0 h-full">
            <Flex
              direction="column"
              gap="2"
              px="2"
              display={{ base: "flex", sm: "none" }}
              _light={{
                bg: "gray.50",
              }}
              _dark={{
                bg: "blackAlpha.200",
              }}
              height="full"
              pt="4"
            >
              {items.map((item) => (
                <SideMenuItem key={item.labelID} item={item} variant="chat" active={item.labelID === "chat"} />
              ))}
            </Flex>
            <ChatListBase w="full" py="4"></ChatListBase>
          </div>
        </DrawerContent>
      </Drawer>
    </>
  );
});
