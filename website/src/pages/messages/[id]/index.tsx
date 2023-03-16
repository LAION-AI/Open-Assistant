import { Box, Card, CardBody } from "@chakra-ui/react";
import { GetServerSideProps, InferGetServerSidePropsType } from "next";
import Head from "next/head";
import { useTranslation } from "next-i18next";
import { serverSideTranslations } from "next-i18next/serverSideTranslations";
import { getDashboardLayout } from "src/components/Layout";
import { MessageLoading } from "src/components/Loading/MessageLoading";
import { MessageTree } from "src/components/Messages/MessageTree";
import { get } from "src/lib/api";
import { Message, MessageWithChildren } from "src/types/Conversation";
import useSWRImmutable from "swr/immutable";

const MessageDetail = ({ id }: InferGetServerSidePropsType<typeof getServerSideProps>) => {
  const { t } = useTranslation(["message", "common"]);
  const { data, isLoading, error } = useSWRImmutable<{ tree: MessageWithChildren | null; message?: Message }>(
    `/api/messages/${id}/tree`,
    get,
    {
      keepPreviousData: true,
    }
  );

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
        <Card>
          <CardBody p={[3, 4, 6]}>
            {isLoading && !data && <MessageLoading></MessageLoading>}
            {error && "Unable to load message tree"}
            {data &&
              (data.tree === null ? (
                "Unable to build tree"
              ) : (
                <MessageTree tree={data.tree} messageId={data.message?.id} scrollToHighlighted />
              ))}
          </CardBody>
        </Card>
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
