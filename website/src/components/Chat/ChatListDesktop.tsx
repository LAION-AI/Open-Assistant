import { ChatListBase } from "./ChatListBase";

const display = { base: "none", lg: "flex" };

export const ChatListDesktop = () => {
  return <ChatListBase pt="4" display={display} w="full" maxW="270px"></ChatListBase>;
};
