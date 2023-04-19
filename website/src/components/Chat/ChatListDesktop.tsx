import { memo } from "react";

import { ChatListBase } from "./ChatListBase";

export const ChatListDesktop = memo(function ChatListDesktop() {
  return <ChatListBase pt="4" display={{ base: "none", lg: "flex" }} w="full" maxW="270px"></ChatListBase>;
});
