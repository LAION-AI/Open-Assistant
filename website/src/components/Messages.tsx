import { Box, forwardRef, Grid, useColorMode } from "@chakra-ui/react";
import { useMemo } from "react";
import { Message } from "src/types/Conversation";

import { FlaggableElement } from "./FlaggableElement";

export const Messages = ({ messages, post_id }: { messages: Message[]; post_id: string }) => {
  const items = messages.map((messageProps: Message, i: number) => {
    const { message_id, text } = messageProps;
    return (
      <FlaggableElement text={text} post_id={post_id} message_id={message_id} key={i + text}>
        <MessageView {...messageProps} />
      </FlaggableElement>
    );
  });
  // Maybe also show a legend of the colors?
  return <Grid gap={2}>{items}</Grid>;
};

export const MessageView = forwardRef<Message, "div">(({ is_assistant, text }: Message, ref) => {
  const { colorMode } = useColorMode();

  const bgColor = useMemo(() => {
    if (colorMode === "light") {
      return is_assistant ? "gray.800" : "blue.600";
    } else {
      return is_assistant ? "black" : "blue.600";
    }
  }, [colorMode, is_assistant]);

  return (
    <Box bg={bgColor} ref={ref} className={`p-4 rounded-md text-white whitespace-pre-wrap`}>
      {text}
    </Box>
  );
});

MessageView.displayName = "MessageView";
