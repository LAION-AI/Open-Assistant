import { Box, CircularProgress, SimpleGrid, Text, useColorModeValue } from "@chakra-ui/react";
import Head from "next/head";
import { useTranslation } from "next-i18next";
import { getDashboardLayout } from "src/components/Layout";
import { MessageTable } from "src/components/Messages/MessageTable";
import { get } from "src/lib/api";
import useSWRImmutable from "swr/immutable";
export { getDefaultStaticProps as getStaticProps } from "src/lib/default_static_props";

const MessagesDashboard = () => {
  const { t } = useTranslation(["message"]);
  const boxBgColor = useColorModeValue("white", "gray.800");
  const boxAccentColor = useColorModeValue("gray.200", "gray.900");

  const { data: messages } = useSWRImmutable("/api/messages", get, { revalidateOnMount: true });
  const { data: userMessages } = useSWRImmutable(`/api/messages/user`, get, { revalidateOnMount: true });

  return (
    <>
      <Head>
        <title>Messages - Open Assistant</title>
        <meta name="description" content="Chat with Open Assistant and provide feedback." />
      </Head>
      <SimpleGrid columns={[1, 1, 1, 1, 1, 2]} gap={4}>
        <Box>
          <Text className="text-2xl font-bold" pb="4">
            {t("recent_messages")}
          </Text>
          <Box
            backgroundColor={boxBgColor}
            boxShadow="base"
            dropShadow={boxAccentColor}
            borderRadius="xl"
            className="p-3 sm:p-4 shadow-sm"
          >
            {messages ? <MessageTable enableLink messages={messages} /> : <CircularProgress isIndeterminate />}
          </Box>
        </Box>
        <Box>
          <Text className="text-2xl font-bold" pb="4">
            {t("your_recent_messages")}
          </Text>
          <Box
            backgroundColor={boxBgColor}
            boxShadow="base"
            dropShadow={boxAccentColor}
            borderRadius="xl"
            className="p-6 shadow-sm"
          >
            {userMessages ? <MessageTable enableLink messages={userMessages} /> : <CircularProgress isIndeterminate />}
          </Box>
        </Box>
      </SimpleGrid>
    </>
  );
};

MessagesDashboard.getLayout = getDashboardLayout;

export default MessagesDashboard;
