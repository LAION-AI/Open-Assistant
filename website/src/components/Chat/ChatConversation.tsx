import { Box, Button, Flex, Textarea, useColorModeValue } from "@chakra-ui/react";
import { useTranslation } from "next-i18next";
import { useCallback, useRef, useState } from "react";
import { InferenceMessage, InferenceResponse } from "src/types/Chat";

interface ChatConversationProps {
  chatId: string;
}

export const ChatConversation = ({ chatId }: ChatConversationProps) => {
  const { t } = useTranslation("common");
  const inputRef = useRef<HTMLTextAreaElement>();
  const [messages, setMessages] = useState<InferenceMessage[]>([]);
  const [streamedResponse, setResponse] = useState("");

  const isLoading = Boolean(streamedResponse);

  const send = useCallback(async () => {
    const content = inputRef.current.value.trim();

    if (!content || !chatId) {
      return;
    }

    setResponse("...");

    const parent_id = messages[messages.length - 1]?.id ?? null;
    // we have to do this manually since we want to stream the chunks
    // there is also EventSource, but it only works with get requests.
    const { body } = await fetch("/api/chat/message", {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify({ chat_id: chatId, content, parent_id }),
    });

    // first chunk is message information
    const stream = iteratorSSE(body);
    const { value } = await stream.next();
    const response: InferenceResponse = JSON.parse(value.data);

    setMessages((messages) => [...messages, response.prompter_message]);

    // remaining messages are the tokens
    let responseMessage = "";
    for await (const { data } of stream) {
      const text = JSON.parse(data).token.text;
      responseMessage += text;
      setResponse(responseMessage);
      // wait for re-render
      await new Promise(requestAnimationFrame);
    }

    setMessages((old) => [...old, { ...response.assistant_message, content: responseMessage }]);
    setResponse(null);
  }, [chatId, messages]);

  return (
    <Flex flexDir="column" gap={4} overflowY="auto">
      {messages.map((message) => (
        <Entry key={message.id} isAssistant={message.role === "assistant"}>
          {message.content}
        </Entry>
      ))}
      {streamedResponse ? <Entry isAssistant>{streamedResponse}</Entry> : <Textarea ref={inputRef} autoFocus />}
      <Button onClick={send} isDisabled={isLoading}>
        {t("submit")}
      </Button>
    </Flex>
  );
};

const Entry = ({ children, isAssistant }) => {
  const bgUser = useColorModeValue("gray.100", "gray.700");
  const bgAssistant = useColorModeValue("#DFE8F1", "#42536B");
  return (
    <Box bg={isAssistant ? bgAssistant : bgUser} borderRadius="lg" p="4" whiteSpace="pre-line">
      {children}
    </Box>
  );
};

async function* iteratorSSE(stream: ReadableStream<Uint8Array>) {
  const reader = stream.pipeThrough(new TextDecoderStream()).getReader();

  let done = false,
    value = "";
  while (!done) {
    ({ value, done } = await reader.read());
    if (done) {
      break;
    }

    const fields = value
      .split(/\r?\n/)
      .filter(Boolean)
      .map((line) => {
        const colonIdx = line.indexOf(":");
        return [line.slice(0, colonIdx), line.slice(colonIdx + 1).trimStart()];
      });
    yield Object.fromEntries(fields);
  }
}
