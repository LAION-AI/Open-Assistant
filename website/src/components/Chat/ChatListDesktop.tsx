import { Box } from "@chakra-ui/react";
import { memo } from "react";

import { ChatListBase } from "./ChatListBase";

// eslint-disable-next-line react/display-name
export const ChatListDesktop = memo(() => {
  return (
    <Box pe="260px" display={{ base: "none", md: "block" }}>
      <ChatListBase></ChatListBase>
    </Box>
  );
});
