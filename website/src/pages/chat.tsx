import { Box, Button, Flex, Textarea, useColorModeValue } from "@chakra-ui/react";
import Head from "next/head";
import { useTranslation } from "next-i18next";
import { useCallback, useEffect, useRef, useState } from "react";
import { getDashboardLayout } from "src/components/Layout";
import { get, post } from "src/lib/api";
export { getDefaultStaticProps as getStaticProps } from "src/lib/default_static_props";
import useSWRMutation from "swr/mutation";

const Chat = () => {
  const inputRef = useRef<HTMLTextAreaElement>();
  const [messages, setMessages] = useState<string[]>([]);
  const [activeMessage, setActiveMessage] = useState("");
  const { trigger: createChat, data: createChatResponse } = useSWRMutation<{ id: string }>("/api/chat", post);

  const chatID = createChatResponse?.id;

  const send = useCallback(async () => {
    const message = inputRef.current.value.trim();

    if (!message || !chatID) {
      return;
    }

    setActiveMessage("...");
    setMessages((old) => [...old, message]);

    // we have to do this manually since we want to stream the chunks
    // there is also EventSource, but it only works with get requests.
    const { body } = await fetch("/api/chat/message", {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify({ id: chatID, message }),
    });

    let responseMessage = "";
    for await (const { data } of iterator(body)) {
      const text = JSON.parse(data).token.text;
      responseMessage += text;
      setActiveMessage(responseMessage);
      // wait for re-render
      await new Promise(requestAnimationFrame);
    }

    setMessages((old) => [...old, responseMessage]);
    setActiveMessage(null);
  }, [chatID]);

  return (
    <>
      <Head>
        <meta name="description" content="Chat with Open Assistant and provide feedback." key="description" />
      </Head>
      <Flex flexDir="column" gap={4} overflowY="auto">
        {!chatID && <Button onClick={() => createChat()}>Create Chat</Button>}
        {chatID && (
          <>
            chat id: {chatID}
            {messages.map((message, idx) => (
              <Entry key={idx} isAssistant={idx % 2 === 1}>
                {message}
              </Entry>
            ))}
            {activeMessage ? (
              <Entry isAssistant>{activeMessage}</Entry>
            ) : (
              <>
                <Textarea ref={inputRef} />
                <Button onClick={send}>Send</Button>
              </>
            )}
          </>
        )}
      </Flex>
    </>
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

async function* iterator(stream: ReadableStream<Uint8Array>) {
  const reader = stream.pipeThrough(new TextDecoderStream()).getReader();

  let done = false,
    value = "";
  while (!done) {
    ({ value, done } = await reader.read());
    if (done) {
      break;
    }

    const fields = value
      .split("\n")
      .filter(Boolean)
      .map((line) => {
        const colonIdx = line.indexOf(":");
        return [line.slice(0, colonIdx), line.slice(colonIdx + 1).trimStart()];
      });
    yield Object.fromEntries(fields);
  }
}

Chat.getLayout = getDashboardLayout;

export default Chat;
