import { Box, Flex } from "@chakra-ui/react";

import { ChatListDesktop } from "../Chat/ChatListDesktop";
import { ChatListMobile } from "../Chat/ChatListMobile";
import { SlimFooter } from "../Dashboard/SlimFooter";
import { Header, HeaderLayout } from "../Header/Header";
import { getDashBoardLayoutSidebarItem } from "../Layout";
import { SideMenuItem } from "../SideMenu";
import { SideMenuLayout } from "../SideMenuLayout";
import { ToSWrapper } from "../ToSWrapper";

export const getChatLayout = (page: React.ReactElement) => (
  <HeaderLayout preLogoSlot={<ChatListMobile />}>
    <ToSWrapper>
      <SideMenuLayout items={getDashBoardLayoutSidebarItem()}>
        <Flex gap={{ md: 4, lg: 6 }}>
          <ChatListDesktop></ChatListDesktop>
          <Box flexGrow="1">
            <Box>{page}</Box>
            <Box mt="10">
              <SlimFooter />
            </Box>
          </Box>
        </Flex>
      </SideMenuLayout>
    </ToSWrapper>
  </HeaderLayout>
);

export const getNewChatLayout = (page: React.ReactElement) => (
  <div className="min-h-screen h-screen max-h-screen flex flex-col overflow-hidden">
    <Header fixed={false} preLogoSlot={<ChatListMobile />}></Header>
    <ToSWrapper>
      <div className="flex min-h-0">
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
          {getDashBoardLayoutSidebarItem().map((item) => (
            <SideMenuItem key={item.labelID} item={item} variant="chat" active={item.labelID === "chat"}></SideMenuItem>
          ))}
        </Flex>
        <ChatListDesktop></ChatListDesktop>
        {page}
      </div>
    </ToSWrapper>
  </div>
);
