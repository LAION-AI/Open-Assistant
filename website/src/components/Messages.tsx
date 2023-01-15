import { Box, forwardRef, Grid, useColorMode } from "@chakra-ui/react";
import { useMemo } from "react";
import { Message } from "src/types/Conversation";

import { FlaggableElement } from "./FlaggableElement";

interface MessagesProps {
  messages: Message[];
}

export const Messages = ({ messages }: MessagesProps) => {
  const items = messages.map((messageProps: Message, i: number) => {
    return (
      <FlaggableElement message={messageProps} key={i + messageProps.id}>
        <MessageView {...messageProps} />
      </FlaggableElement>
    );
  });
  // Maybe also show a legend of the colors?
  return <Grid gap={2}>{items}</Grid>;
};

export const MessageView = forwardRef<Message, "div">((message: Message, ref) => {
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
