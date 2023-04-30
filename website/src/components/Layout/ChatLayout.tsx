import { Flex } from "@chakra-ui/react";
import { PropsWithChildren } from "react";
import { useSidebarItems } from "src/hooks/layout/sidebarItems";

import { ChatListDesktop } from "../Chat/ChatListDesktop";
import { ChatListMobile } from "../Chat/ChatListMobile";
import { Header } from "../Header/Header";
import { SideMenuItem } from "../SideMenu";
import { ToSWrapper } from "../ToSWrapper";

export const ChatLayout = ({ children }: PropsWithChildren) => (
  <div className="min-h-screen h-screen max-h-screen flex flex-col overflow-hidden">
    <Header fixed={false} preLogoSlot={<ChatListMobile />}></Header>
    <ToSWrapper>
      <div className="flex min-h-0 h-full">
        <Flex
          direction="column"
          gap="2"
          px="2"
          display={{ base: "none", sm: "flex" }}
          _light={{
            bg: "gray.50",
          }}
          _dark={{
            bg: "blackAlpha.200",
          }}
          height="full"
          pt="4"
        >
          {useSidebarItems().map((item) => (
            <SideMenuItem key={item.labelID} item={item} variant="chat" active={item.labelID === "chat"}></SideMenuItem>
          ))}
        </Flex>
        <ChatListDesktop />
        {children}
      </div>
    </ToSWrapper>
  </div>
);
