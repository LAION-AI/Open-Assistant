import { Box, Flex } from "@chakra-ui/react";

import { ChatListDesktop } from "../Chat/ChatListDesktop";
import { ChatListMobile } from "../Chat/ChatListMobile";
import { SlimFooter } from "../Dashboard/SlimFooter";
import { HeaderLayout } from "../Header/Header";
import { getDashBoardLayoutSidebarItem } from "../Layout";
import { SideMenuLayout } from "../SideMenuLayout";
import { ToSWrapper } from "../ToSWrapper";

export const getChatLayout = (page: React.ReactElement) => (
  <HeaderLayout preLogoSlot={<ChatListMobile />}>
    <ToSWrapper>
      <SideMenuLayout collapsed items={getDashBoardLayoutSidebarItem()}>
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
