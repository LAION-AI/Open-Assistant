import { Box, CircularProgress, SimpleGrid, Text, useColorModeValue } from "@chakra-ui/react";
import Head from "next/head";
import { useState } from "react";
import useSWRImmutable from "swr/immutable";

import fetcher from "src/lib/fetcher";
import { SideMenu } from "src/components/Dashboard";
import { MessageTable } from "src/components/Messages/MessageTable";
import { getDashboardLayout } from "src/components/Layout";
import { colors } from "styles/Theme/colors";

const MessagesDashboard = () => {
  const bgColor = useColorModeValue(colors.light.bg, colors.dark.bg);
  const boxBgColor = useColorModeValue("white", "gray.700");
  const boxAccentColor = useColorModeValue("gray.200", "gray.900");

  const [messages, setMessages] = useState([]);
  const [userMessages, setUserMessages] = useState([]);

  const { isLoading: isLoadingAll } = useSWRImmutable("/api/messages", fetcher, {
    onSuccess: (data) => {
      setMessages(data);
    },
  });

  const { isLoading: isLoadingUser } = useSWRImmutable(`/api/messages/user`, fetcher, {
    onSuccess: (data) => {
      setUserMessages(data);
    },
  });

  return (
    <>
      <Head>
        <title>Messages - Open Assistant</title>
        <meta name="description" content="Chat with Open Assistant and provide feedback." />
      </Head>
      <Box backgroundColor={bgColor} className="sm:overflow-hidden">
        <Box className="sm:flex h-full gap-6">
          <Box className="p-6 sm:pr-0">
            <SideMenu />
          </Box>
          <Box className="flex flex-col overflow-auto p-6 sm:pl-0 gap-14">
            <SimpleGrid columns={[1, 1, 1, 2]} spacing={2}>
              <Box>
                <Text className="text-2xl font-bold">Most recent messages</Text>
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
                <Text className="text-2xl font-bold">Your most recent messages</Text>
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
          </Box>
        </Box>
      </Box>
    </>
  );
};

MessagesDashboard.getLayout = (page) => getDashboardLayout(page);

export default MessagesDashboard;
