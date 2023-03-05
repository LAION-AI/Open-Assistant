import { HStack } from "@chakra-ui/react";
import { ReactNode } from "react";

export const MessageInlineEmojiRow = ({ children }: { children: ReactNode }) => {
  return (
    <HStack
      justifyContent="end"
      style={{ position: "relative", right: "-0.3em", bottom: "-0em", marginLeft: "1em" }}
      onClick={(e) => e.stopPropagation()}
    >
      {children}
    </HStack>
  );
};
