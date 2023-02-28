import { Card, CardBody, CardHeader, CircularProgress, Grid } from "@chakra-ui/react";
import { GetServerSideProps } from "next";
import Head from "next/head";
import { useRouter } from "next/router";
import { serverSideTranslations } from "next-i18next/serverSideTranslations";
import { AdminArea } from "src/components/AdminArea";
import { JsonCard } from "src/components/JsonCard";
import { getAdminLayout } from "src/components/Layout";
import { MessageTree } from "src/components/Messages/MessageTree";
import { get } from "src/lib/api";
import { Message, MessageWithChildren } from "src/types/Conversation";
import useSWRImmutable from "swr/immutable";

const MessageDetail = () => {
  const router = useRouter();
  const messageId = router.query.id;
  const { data, isLoading, error } = useSWRImmutable<{
    tree: MessageWithChildren | null;
    message?: Message;
  }>(`/api/admin/messages/${messageId}/tree`, get);

  return (
    <>
      <Head>
        <title>Open Assistant</title>
      </Head>
      <AdminArea>
        {isLoading && <CircularProgress isIndeterminate></CircularProgress>}
        {error && "Unable to load message tree"}
        {data &&
          (data.tree === null ? (
            "Unable to build tree"
          ) : (
            <Grid gap="6">
              <Card>
                <CardHeader fontWeight="bold" fontSize="xl" pb="0">
                  Message Detail
                </CardHeader>
                <CardBody>
                  <JsonCard>{data.message}</JsonCard>
                </CardBody>
              </Card>
              <Card>
                <CardHeader fontWeight="bold" fontSize="xl" pb="0">
                  Tree {data.tree.id}
                </CardHeader>
                <CardBody>
                  <MessageTree tree={data.tree} messageId={data.message?.id} scrollToHighlighted />
                </CardBody>
              </Card>
            </Grid>
          ))}
      </AdminArea>
    </>
  );
};

MessageDetail.getLayout = getAdminLayout;

export default MessageDetail;

export const getServerSideProps: GetServerSideProps = async ({ locale = "en" }) => {
  return {
    props: {
      ...(await serverSideTranslations(locale, ["common", "labelling", "message"])),
    },
  };
};
