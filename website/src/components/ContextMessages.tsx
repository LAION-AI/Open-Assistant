import { Box } from "@chakra-ui/react";
import { Message } from "src/components/Messages";

export const ContextMessages = ({ messages }: { messages: Message[] }) => {
  return (
    <Box className="flex flex-col gap-1">
      {messages.map((message, i) => {
        return (
          <Box key={i}>
            <span>{message.is_assistant ? "Assistant: " : "User: "}</span>
            <span>{message.text}</span>
          </Box>
        );
      })}
    </Box>
  );
};
