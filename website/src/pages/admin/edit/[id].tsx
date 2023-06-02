import {
  Box,
  Button,
  Card,
  CardBody,
  Flex,
  Stack,
  Tab,
  TabList,
  TabPanel,
  TabPanels,
  Tabs,
  Text,
  useColorModeValue,
} from "@chakra-ui/react";
import { GetServerSideProps, InferGetServerSidePropsType } from "next";
import Head from "next/head";
import { useTranslation } from "next-i18next";
import { serverSideTranslations } from "next-i18next/serverSideTranslations";
import { lazy, Suspense, useEffect, useMemo, useState } from "react";
import { AdminArea } from "src/components/AdminArea";
import { AdminLayout } from "src/components/Layout";
import { MessageLoading } from "src/components/Loading/MessageLoading";
import { MessageTree } from "src/components/Messages/MessageTree";
import { TrackedTextarea } from "src/components/Survey/TrackedTextarea";
import { TwoColumnsWithCards } from "src/components/Survey/TwoColumnsWithCards";
import { get } from "src/lib/api";
import { Message, MessageWithChildren } from "src/types/Conversation";
import useSWRImmutable from "swr/immutable";

const RenderedMarkdown = lazy(() => import("../../../components/Messages/RenderedMarkdown"));

const EditMessage = ({ id }: InferGetServerSidePropsType<typeof getServerSideProps>) => {
  const [messageText, setMessageText] = useState("");
  const { t } = useTranslation(["common", "tasks"]);
  const { data, isLoading, error } = useSWRImmutable<{ tree: MessageWithChildren | null; message?: Message }>(
    `/api/admin/messages/${id}/tree`,
    get,
    { keepPreviousData: true }
  );

  useEffect(() => {
    if (data && data.message) {
      setMessageText(data.message.text);
    }
  }, [data]);

  const previewContent = useMemo(
    () => (
      <Suspense fallback={messageText}>
        <RenderedMarkdown markdown={messageText}></RenderedMarkdown>
      </Suspense>
    ),
    [messageText]
  );

  const getThreadFromTree = (tree: MessageWithChildren | null, targetMessageId: string) => {
    if (!tree) {
      return null;
    }

    if (tree.id === targetMessageId) {
      return tree;
    }

    const filtered_children: (MessageWithChildren | null)[] = tree.children
      .map((child) => getThreadFromTree(child, targetMessageId))
      .filter((child) => child);
    return filtered_children.length ? { ...tree, children: filtered_children } : null;
  };

  const messageThread = getThreadFromTree(data?.tree, id);
  const titleColor = useColorModeValue("gray.800", "gray.300");
  const labelColor = useColorModeValue("gray.600", "gray.400");
  const cardColor = useColorModeValue("gray.50", "gray.800");

  return (
    <>
      <Head>
        <title>{t("common:title")}</title>
        <meta name="description" content={t("common:conversational")} />
      </Head>
      {(isLoading || !data) && (
        <Card>
          <CardBody>
            <MessageLoading />
          </CardBody>
        </Card>
      )}
      {error && "Unable to load message tree"}
      {!isLoading && data && (
        <AdminArea>
          <TwoColumnsWithCards>
            <>
              <Stack spacing={1}>
                <Text fontSize="xl" fontWeight="bold" color={titleColor}>
                  {t("common:edit")}
                </Text>
                <Text fontSize="md" color={labelColor}>
                  {t("tasks:moderator_edit_explain")}
                </Text>
              </Stack>
              <Box marginTop={4} borderRadius={"lg"} backgroundColor={cardColor} className="p-3 sm:p-6">
                {!messageThread ? (
                  "Unable to build tree"
                ) : (
                  <MessageTree tree={messageThread} messageId={data.message?.id} />
                )}
              </Box>
            </>
            <>
              <Stack spacing={1}>
                <Tabs isLazy>
                  <TabList>
                    <Tab>{t("tasks:tab_write")}</Tab>
                    <Tab>{t("tasks:tab_preview")}</Tab>
                  </TabList>
                  <TabPanels>
                    <TabPanel>
                      <TrackedTextarea
                        text={messageText}
                        onTextChange={setMessageText}
                        thresholds={{ low: 20, medium: 40, goal: 50 }}
                        textareaProps={{ minRows: 5 }}
                      />
                    </TabPanel>
                    <TabPanel p="0" pt="4" marginBottom={2}>
                      {previewContent}
                    </TabPanel>
                  </TabPanels>
                </Tabs>
                <Flex justify={"flex-start"}>
                  <Button size="lg" variant="solid" colorScheme="green">
                    {t("common:submit")}
                  </Button>
                </Flex>
              </Stack>
            </>
          </TwoColumnsWithCards>
        </AdminArea>
      )}
    </>
  );
};

EditMessage.getLayout = AdminLayout;

export const getServerSideProps: GetServerSideProps<{ id: string }, { id: string }> = async ({
  locale = "en",
  params,
}) => ({
  props: {
    // eslint-disable-next-line @typescript-eslint/no-non-null-assertion
    id: params!.id,
    ...(await serverSideTranslations(locale, ["common", "message", "labelling", "tasks"])),
  },
});

export default EditMessage;
