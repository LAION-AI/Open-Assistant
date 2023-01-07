import { Box, CircularProgress, SimpleGrid, Text, useColorModeValue } from "@chakra-ui/react";
import Head from "next/head";
import { useEffect, useState } from "react";
import { getDashboardLayout } from "src/components/Layout";
import { MessageTable } from "src/components/Messages/MessageTable";
import fetcher from "src/lib/fetcher";
import useSWRImmutable from "swr/immutable";

const MessagesDashboard = () => {
  const boxBgColor = useColorModeValue("white", "gray.700");
  const boxAccentColor = useColorModeValue("gray.200", "gray.900");

  const [messages, setMessages] = useState([]);
  const [userMessages, setUserMessages] = useState([]);

  const { isLoading: isLoadingAll, mutate: mutateAll } = useSWRImmutable("/api/messages", fetcher, {
    onSuccess: (data) => {
      setMessages(data);
    },
  });

  const { isLoading: isLoadingUser, mutate: mutateUser } = useSWRImmutable(`/api/messages/user`, fetcher, {
    onSuccess: (data) => {
      setUserMessages(data);
    },
  });

  useEffect(() => {
    if (messages.length == 0) {
      mutateAll();
    }
    if (userMessages.length == 0) {
      mutateUser();
    }
  }, [messages, userMessages]);

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
            {isLoadingAll ? <CircularProgress isIndeterminate /> : <MessageTable messages={messages} />}
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
            {isLoadingUser ? <CircularProgress isIndeterminate /> : <MessageTable messages={userMessages} />}
          </Box>
        </Box>
      </SimpleGrid>
    </>
  );
};

MessagesDashboard.getLayout = (page) => getDashboardLayout(page);

export default MessagesDashboard;
