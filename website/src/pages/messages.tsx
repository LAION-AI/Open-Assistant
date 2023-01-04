import {
  Avatar,
  Box,
  CircularProgress,
  HStack,
  SimpleGrid,
  Stack,
  StackDivider,
  Text,
  useColorModeValue,
} from "@chakra-ui/react";
import Head from "next/head";
import { useState } from "react";
import useSWRImmutable from "swr/immutable";

import fetcher from "src/lib/fetcher";
import { SideMenu } from "src/components/Dashboard";
import { FlaggableElement } from "src/components/FlaggableElement";
import { Header } from "src/components/Header";
import { colors } from "styles/Theme/colors";

const MessageTable = ({ messages, isLoading }) => {
  const backgroundColor = useColorModeValue("white", "gray.700");
  const accentColor = useColorModeValue("gray.200", "gray.900");

  return (
    <Box
      backgroundColor={backgroundColor}
      boxShadow="base"
      dropShadow={accentColor}
      borderRadius="xl"
      className="p-6 shadow-sm"
    >
      {isLoading ? (
        <CircularProgress isIndeterminate />
      ) : (
        <Stack divider={<StackDivider />} spacing="4">
          {messages.map((item, idx) => (
            <MesssageTableEntry item={item} idx={idx} key={item.id} />
          ))}
        </Stack>
      )}
    </Box>
  );
};

const MesssageTableEntry = ({ item, idx }) => {
  const bgColor = useColorModeValue(idx % 2 === 0 ? "bg-slate-800" : "bg-black", "bg-sky-900");

  return (
    <FlaggableElement text={item.text} post_id={item.id} key={`flag_${item.id}`}>
      <HStack>
        <Avatar
          name={`${item.isAssistant ? "Assitant" : "User"}`}
          src={`${item.isAssistant ? "/logos/logo.png" : "/images/temp-avatars/av1.jpg"}`}
        />
        <Box className={`p-4 rounded-md text-white whitespace-pre-wrap ${bgColor} text-white w-full`}>{item.text}</Box>
      </HStack>
    </FlaggableElement>
  );
};

const MessagesDashboard = () => {
  const bgColor = useColorModeValue(colors.light.bg, colors.dark.bg);

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
            <SimpleGrid columns={2} spacing={2}>
              <Box>
                <Text className="text-2xl font-bold">Most recent messages</Text>
                <MessageTable messages={messages} isLoading={isLoadingAll} />
              </Box>
              <Box>
                <Text className="text-2xl font-bold">Your most recent messages</Text>
                <MessageTable messages={userMessages} isLoading={isLoadingUser} />
              </Box>
            </SimpleGrid>
          </Box>
        </Box>
      </Box>
    </>
  );
};

MessagesDashboard.getLayout = (page) => (
  <div className="grid grid-rows-[min-content_1fr_min-content] h-full justify-items-stretch">
    <Header transparent={true} />
    {page}
  </div>
);

export default MessagesDashboard;
