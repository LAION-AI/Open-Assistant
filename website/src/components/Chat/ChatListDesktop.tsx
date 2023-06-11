import { Box } from "@chakra-ui/react";
import { ChatListBase } from "./ChatListBase";

const display = { base: "none", lg: "flex" };

export const ChatListDesktop = () => {
  return (
    <Box zIndex="var(--chakra-zIndices-docked)">
      <ChatListBase pt="4" display={display} w="full" maxW="270px"></ChatListBase>
    </Box>
  );
};
