import { HStack } from "@chakra-ui/react";
import { ReactNode, SyntheticEvent } from "react";

const stopPropagation = (e: SyntheticEvent) => e.stopPropagation();

export const MessageInlineEmojiRow = ({ children }: { children: ReactNode }) => {
  return (
    <HStack justifyContent="end" pos="relative" onClick={stopPropagation}>
      {children}
    </HStack>
  );
};
