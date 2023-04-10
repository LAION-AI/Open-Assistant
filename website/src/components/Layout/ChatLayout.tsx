import { Box, Flex } from "@chakra-ui/react";
import { BarChart2, ExternalLink, Layout, MessageCircle, MessageSquare, TrendingUp } from "lucide-react";
import { getEnv } from "src/lib/browserEnv";

import { ChatList } from "../Chat/ChatList";
import { ChatListMobile } from "../Chat/ChatListMobile";
import { SlimFooter } from "../Dashboard/SlimFooter";
import { HeaderLayout } from "../Header/Header";
import { SideMenuLayout } from "../SideMenuLayout";
import { ToSWrapper } from "../ToSWrapper";

export const getChatLayout = (page: React.ReactElement) => (
  <HeaderLayout preLogoSlot={<ChatListMobile />}>
    <ToSWrapper>
      <SideMenuLayout
        collapsed
        items={[
          {
            labelID: "dashboard",
            pathname: "/dashboard",
            icon: Layout,
          },
          {
            labelID: "messages",
            pathname: "/messages",
            icon: MessageSquare,
          },
          {
            labelID: "leaderboard",
            pathname: "/leaderboard",
            icon: BarChart2,
          },
          {
            labelID: "stats",
            pathname: "/stats",
            icon: TrendingUp,
          },
          ...(getEnv().ENABLE_CHAT
            ? [
                {
                  labelID: "chat",
                  pathname: "/chat",
                  icon: MessageCircle,
                },
              ]
            : []),
          {
            labelID: "guidelines",
            pathname: "https://projects.laion.ai/Open-Assistant/docs/guides/guidelines",
            icon: ExternalLink,
            target: "_blank",
          },
        ]}
      >
        <Flex gap={{ md: 4, lg: 6 }}>
          <ChatList></ChatList>
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
