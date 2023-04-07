import { HStack } from "@chakra-ui/react";
import { ReactNode } from "react";

const stopPropagation = (e) => e.stopPropagation();

export const MessageInlineEmojiRow = ({ children }: { children: ReactNode }) => {
  return (
    <HStack justifyContent="end" pos="relative" onClick={stopPropagation}>
      {children}
    </HStack>
  );
};
