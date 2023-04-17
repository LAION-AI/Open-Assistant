import { Box } from "@chakra-ui/react";
import { memo } from "react";

import { ChatListBase } from "./ChatListBase";

export const ChatListDesktop = memo(function ChatListDesktop() {
  return (
    <Box pe="260px" display={{ base: "none", md: "block" }}>
      <ChatListBase isSideBar />
    </Box>
  );
});
