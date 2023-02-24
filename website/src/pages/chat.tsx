import { Box, Button, Flex, Textarea, useColorModeValue } from "@chakra-ui/react";
import Head from "next/head";
import { useTranslation } from "next-i18next";
import { useCallback, useRef, useState } from "react";
import { getDashboardLayout } from "src/components/Layout";
import { post } from "src/lib/api";
export { getDefaultStaticProps as getStaticProps } from "src/lib/default_static_props";
import { Flags } from "react-feature-flags";
import useSWRMutation from "swr/mutation";

const Chat = () => {
  const { t } = useTranslation("common");
  const inputRef = useRef<HTMLTextAreaElement>();
  const [messages, setMessages] = useState<InferenceMessage[]>([]);
  const [activeMessage, setActiveMessage] = useState("");
  const { trigger: createChat, data: createChatResponse } = useSWRMutation<{ id: string }>("/api/chat", post);

  const chatID = createChatResponse?.id;
  const isLoading = Boolean(activeMessage);

  const send = useCallback(async () => {
    const content = inputRef.current.value.trim();

    if (!content || !chatID) {
      return;
    }

    setActiveMessage("...");

    const parent_id = messages[messages.length - 1]?.id ?? null;
    // we have to do this manually since we want to stream the chunks
    // there is also EventSource, but it only works with get requests.
    const { body } = await fetch("/api/chat/message", {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify({ chat_id: chatID, content, parent_id }),
    });

    // first chunk is message information
    const stream = iterator(body);
    const { value } = await stream.next();
    const response: InferenceResponse = JSON.parse(value.data);

    setMessages((messages) => [...messages, response.prompter_message]);

    // remaining messages are the tokens
    let responseMessage = "";
    for await (const { data } of stream) {
      const text = JSON.parse(data).token.text;
      responseMessage += text;
      setActiveMessage(responseMessage);
      // wait for re-render
      await new Promise(requestAnimationFrame);
    }

    setMessages((old) => [...old, { ...response.assistant_message, content: responseMessage }]);
    setActiveMessage(null);
  }, [chatID, messages]);

  return (
    <>
      <Head>
        <title>{t("chat")}</title>
      </Head>

      <Flags authorizedFlags={["chatEnabled"]}>
        <Flex flexDir="column" gap={4} overflowY="auto">
          {!chatID && <Button onClick={() => createChat()}>{t("create_chat")}</Button>}
          {chatID && (
            <>
              {messages.map((message) => (
                <Entry key={message.id} isAssistant={message.role === "assistant"}>
                  {message.content}
                </Entry>
              ))}
              {activeMessage ? <Entry isAssistant>{activeMessage}</Entry> : <Textarea ref={inputRef} autoFocus />}
              <Button onClick={send} isDisabled={isLoading}>
                {t("submit")}
              </Button>
            </>
          )}
        </Flex>
      </Flags>
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
      .split(/\r?\n/)
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

interface InferenceResponse {
  assistant_message: InferenceMessage;
  prompter_message: InferenceMessage;
}

interface InferenceMessage {
  id: string;
  content: string | null;
  state: "manual" | "pending";
  role: "assistant" | "prompter";
}
