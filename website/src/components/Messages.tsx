import { Box, forwardRef, useColorMode } from "@chakra-ui/react";
import { useMemo } from "react";
import { Message } from "src/types/Conversation";

export const MessageView = forwardRef<Partial<Message>, "div">((message: Partial<Message>, ref) => {
  const { colorMode } = useColorMode();

  const bgColor = useMemo(() => {
    if (colorMode === "light") {
      return message.is_assistant ? "gray.800" : "blue.600";
    } else {
      return message.is_assistant ? "black" : "blue.600";
    }
  }, [colorMode, message.is_assistant]);

  return (
    <Box bg={bgColor} ref={ref} className={`p-4 rounded-md text-white whitespace-pre-wrap`}>
      {message.text}
    </Box>
  );
});

MessageView.displayName = "MessageView";
