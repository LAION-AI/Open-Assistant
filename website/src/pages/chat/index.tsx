import { Box, Button, Divider, Flex, Grid, Progress, Text } from "@chakra-ui/react";
import { GetServerSideProps } from "next";
import Head from "next/head";
import Link from "next/link";
import { useRouter } from "next/router";
import { useTranslation } from "next-i18next";
import { serverSideTranslations } from "next-i18next/serverSideTranslations";
import React, { useCallback, useMemo } from "react";
import { DeleteChatButton } from "src/components/Chat/DeleteChatButton";
import { getDashboardLayout } from "src/components/Layout";
import { SurveyCard } from "src/components/Survey/SurveyCard";
import { get, post } from "src/lib/api";
import { isChatEnable } from "src/lib/isChatEnable";
import { GetChatsResponse } from "src/types/Chat";
import useSWR from "swr";
import useSWRMutation from "swr/mutation";

export const getServerSideProps: GetServerSideProps = async ({ locale = "en" }) => {
  if (!isChatEnable()) {
    return {
      notFound: true,
    };
  }
  return {
    props: {
      inferenceHost: process.env.INFERENCE_SERVER_HOST,
      ...(await serverSideTranslations(locale)),
    },
  };
};

const Chat = () => {
  const { t } = useTranslation(["common", "chat"]);
  const router = useRouter();

  const { data, mutate: refreshChatList } = useSWR<GetChatsResponse>("/api/chat", get, { revalidateOnFocus: true });
  const { trigger: newChatTrigger } = useSWRMutation<{ id: string }>("/api/chat", post);

  const createChat = useCallback(async () => {
    const chat = await newChatTrigger();
    router.push(`/chat/${chat!.id}`);
  }, [newChatTrigger, router]);

  const content = useMemo(() => {
    if (!data) {
      return <Progress size="sm" isIndeterminate />;
    }
    return (
      <SurveyCard>
        <Flex direction="column" gap="4">
          <Flex justifyContent="space-between" alignItems="center" flexWrap="wrap">
            <Text fontSize="xl" fontWeight="bold">
              {t("chat:your_chats")}
            </Text>
            <Button maxW="2xs" onClick={createChat}>
              {t("create_chat")}
            </Button>
          </Flex>
          <Divider />
          <Grid
            rowGap={1}
            p={2}
            alignItems="center"
            columnGap={[2, 4]}
            gridTemplateColumns={[`auto auto`, `1fr auto auto`]}
          >
            {data.chats.map(({ id, modified_at, title }) => (
              <React.Fragment key={id}>
                <Text
                  as={Button}
                  bg="inherit"
                  borderRadius="sm"
                  overflowX="hidden"
                  textOverflow="ellipsis"
                  gridColumn={["span 2", "span 1"]}
                >
                  <Link href={`/chat/${id}`} className="w-full h-full text-start flex items-center">
                    {title ?? t("chat:empty")}
                  </Link>
                </Text>
                <Text>
                  {t("chat:chat_date", {
                    val: new Date(modified_at),
                    formatParams: { val: { dateStyle: "short", timeStyle: "short" } },
                  })}
                </Text>
                <DeleteChatButton chatId={id} onDelete={refreshChatList} />
              </React.Fragment>
            ))}
          </Grid>
        </Flex>
      </SurveyCard>
    );
  }, [data, t, createChat, refreshChatList]);

  return (
    <>
      <Head>
        <title>{t("chat")}</title>
      </Head>
      <Box className="max-w-5xl mx-auto">{content}</Box>
    </>
  );
};

Chat.getLayout = getDashboardLayout;

export default Chat;
