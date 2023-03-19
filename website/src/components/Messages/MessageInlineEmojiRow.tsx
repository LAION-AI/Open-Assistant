import { HStack } from "@chakra-ui/react";
import { ReactNode } from "react";

export const MessageInlineEmojiRow = ({ children }: { children: ReactNode }) => {
  return (
    <HStack justifyContent="end" style={{ position: "relative" }} onClick={(e) => e.stopPropagation()}>
      {children}
    </HStack>
  );
};
