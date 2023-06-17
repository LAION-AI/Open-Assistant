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
import { useRouter } from 'next/router';
import { useTranslation } from "next-i18next";
import { serverSideTranslations } from 'next-i18next/serverSideTranslations';
import { lazy, Suspense, useCallback, useEffect, useMemo, useState } from 'react';
import { DashboardLayout } from 'src/components/Layout';
import { MessageLoading } from "src/components/Loading/MessageLoading";
import { get, post } from 'src/lib/api';
import { Message, MessageWithChildren } from 'src/types/Conversation';
import useSWRImmutable from 'swr/immutable';
import { TwoColumnsWithCards } from "src/components/Survey/TwoColumnsWithCards";
import { TrackedTextarea } from "src/components/Survey/TrackedTextarea";
import { MessageTree } from "src/components/Messages/MessageTree";
import { API_ROUTES } from "src/lib/routes";
import useSWRMutation from "swr/mutation";
import { diffChars } from "diff";

const RenderedMarkdown = lazy(() => import('../../../../components/Messages/RenderedMarkdown'));

const CreateRevisionProposal = ({ id }: InferGetServerSidePropsType<typeof getServerSideProps>) => {
  const { t } = useTranslation(["common", "tasks"]);
  const router = useRouter();

  const { trigger: submitRevisionProposal, isMutating: isSubmiting } = useSWRMutation(
    API_ROUTES.PROPOSE_REVISION_TO_MESSAGE(id), 
    post, 
    {
      onSuccess: () => {
        // router.push(ROUTES.ADMIN_MESSAGE_DETAIL(id));
      },
    }
  );

  const { data, isLoading, error } = useSWRImmutable<{ tree: MessageWithChildren | null; message?: Message }>(
    `/api/messages/${id}/tree`,
    get,
    { keepPreviousData: true }
  );

  const [messageText, setMessageText] = useState("");

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
      {error && "Unable to load message tree to propose revision for"}
      {!isLoading && data && (
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
              <MessageTree tree={data.tree} messageId={id} />
            </Box>
          </>
          <>
            <Stack spacing={1}>
              <Tabs isLazy>
                <TabList>
                  <Tab>{t("tasks:tab_write")}</Tab>
                  <Tab>View changes</Tab>
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
                  <TabPanel><h1>TODO</h1></TabPanel>
                  <TabPanel p="0" pt="4" marginBottom={2}>
                    {previewContent}
                  </TabPanel>
                </TabPanels>
              </Tabs>
              <Flex justify={"flex-start"}>
                <Button
                  size="lg"
                  variant="solid"
                  colorScheme="green"
                  onClick={async () => {
                    await submitRevisionProposal({ 
                      arg: {
                        new_content: messageText,
                        changes: diffChars(data.message.text, messageText)
                      } 
                    });
                  }}
                  isLoading={isSubmiting}
                  loadingText={"Submitting"}
                >
                  {t("common:submit")}
                </Button>
              </Flex>
            </Stack>
          </>
        </TwoColumnsWithCards>
      )}
    </>
  );
};

CreateRevisionProposal.getLayout = DashboardLayout;

export const getServerSideProps: GetServerSideProps<{ id: string }, { id: string }> = async ({
  locale = "en",
  params,
}) => ({
  props: {
    id: params!.id,
    ...(await serverSideTranslations(locale))
  }
});

export default CreateRevisionProposal;

