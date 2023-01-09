import { Box, CircularProgress, SimpleGrid, Text, useColorModeValue } from "@chakra-ui/react";
import Head from "next/head";
import { useEffect, useState } from "react";
import { getDashboardLayout } from "src/components/Layout";
import { Message } from "src/components/Messages";
import { MessageTable } from "src/components/Messages/MessageTable";
import fetcher from "src/lib/fetcher";
import useSWRImmutable from "swr/immutable";

const MessagesDashboard = () => {
  const boxBgColor = useColorModeValue("white", "gray.700");
  const boxAccentColor = useColorModeValue("gray.200", "gray.900");

  const [messages, setMessages] = useState<Message[]>(null);
  const [userMessages, setUserMessages] = useState<Message[]>(null);

  const { isLoading: isLoadingAll, mutate: mutateAll } = useSWRImmutable("/api/messages", fetcher, {
    onSuccess: setMessages,
  });

  const { isLoading: isLoadingUser, mutate: mutateUser } = useSWRImmutable(`/api/messages/user`, fetcher, {
    onSuccess: setUserMessages,
  });

  const receivedMessages = !isLoadingAll && Array.isArray(messages);
  const receivedUserMessages = !isLoadingUser && Array.isArray(userMessages);

  useEffect(() => {
    if (!receivedMessages) {
      mutateAll();
    }
    if (!receivedUserMessages) {
      mutateUser();
    }
  }, [receivedMessages, mutateAll, receivedUserMessages, mutateUser]);

  return (
    <>
      <Head>
        <title>Messages - Open Assistant</title>
        <meta name="description" content="Chat with Open Assistant and provide feedback." />
      </Head>
      <SimpleGrid columns={[1, 1, 1, 2]} gap={4}>
        <Box>
          <Text className="text-2xl font-bold" pb="4">
            Most recent messages
          </Text>
          <Box
            backgroundColor={boxBgColor}
            boxShadow="base"
            dropShadow={boxAccentColor}
            borderRadius="xl"
            className="p-6 shadow-sm"
          >
            {receivedMessages ? <MessageTable messages={messages} /> : <CircularProgress isIndeterminate />}
          </Box>
        </Box>
        <Box>
          <Text className="text-2xl font-bold" pb="4">
            Your most recent messages
          </Text>
          <Box
            backgroundColor={boxBgColor}
            boxShadow="base"
            dropShadow={boxAccentColor}
            borderRadius="xl"
            className="p-6 shadow-sm"
          >
            {receivedUserMessages ? <MessageTable messages={userMessages} /> : <CircularProgress isIndeterminate />}
          </Box>
        </Box>
      </SimpleGrid>
    </>
  );
};

MessagesDashboard.getLayout = (page) => getDashboardLayout(page);

export default MessagesDashboard;
