import { Box, Card, Text, useColorModeValue } from "@chakra-ui/react";
import { GetServerSideProps, InferGetServerSidePropsType } from "next";
import Head from "next/head";
import { useTranslation } from "next-i18next";
import { serverSideTranslations } from "next-i18next/serverSideTranslations";
import { getDashboardLayout } from "src/components/Layout";
import { MessageLoading } from "src/components/Loading/MessageLoading";
import { MessageTableEntry } from "src/components/Messages/MessageTableEntry";
import { MessageWithChildren } from "src/components/Messages/MessageWithChildren";
import { get } from "src/lib/api";
import { Message } from "src/types/Conversation";
import useSWRImmutable from "swr/immutable";

const MessageDetail = ({ id }: InferGetServerSidePropsType<typeof getServerSideProps>) => {
  const { t } = useTranslation(["message", "common"]);
  const backgroundColor = useColorModeValue("white", "gray.800");

  const { isLoading: isLoadingParent, data: parent } = useSWRImmutable<Message>(`/api/messages/${id}/parent`, get);

  if (isLoadingParent) {
    return <MessageLoading />;
  }
  return (
    <>
      <Head>
        <title>{t("common:title")}</title>
        <meta
          name="description"
          content="Conversational AI for everyone. An open source project to create a chat enabled GPT LLM run by LAION and contributors around the world."
        />
      </Head>
      <Box width="full">
        {parent && (
          <Box pb="4">
            <Text fontWeight="bold" fontSize="xl" pb="2">
              {t("parent")}
            </Text>
            <Card bg={backgroundColor} padding="4" width="fit-content">
              <MessageTableEntry enabled message={parent} />
            </Card>
          </Box>
        )}
        <Box pb="4">
          <MessageWithChildren id={id} maxDepth={2} />
        </Box>
      </Box>
    </>
  );
};

MessageDetail.getLayout = getDashboardLayout;

export const getServerSideProps: GetServerSideProps<{ id: string }, { id: string }> = async ({
  locale = "en",
  params,
}) => ({
  props: {
    // eslint-disable-next-line @typescript-eslint/no-non-null-assertion
    id: params!.id,
    ...(await serverSideTranslations(locale, ["common", "message", "labelling", "side_menu"])),
  },
});

export default MessageDetail;
