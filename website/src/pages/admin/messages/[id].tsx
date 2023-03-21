import {
  Card,
  CardBody,
  CardHeader,
  CircularProgress,
  Grid,
  Text,
  TableContainer,
  Table,
  TableCaption,
  Thead,
  Tr,
  Th,
  Tbody,
  Td,
} from "@chakra-ui/react";
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
    tree_state: {
      message_tree_id: string;
      state: string;
      active: boolean;
      goal_tree_size: number;
      max_children_count: number;
      max_depth: number;
      origin: string;
    };
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
                  <TableContainer>
                    <Table variant="simple">
                      <TableCaption>Message tree state</TableCaption>
                      <Thead>
                        <Tr>
                          <Th>Property</Th>
                          <Th>Value</Th>
                        </Tr>
                      </Thead>
                      <Tbody>
                        <Tr>
                          <Td>State</Td>
                          <Td>{data.tree_state.state}</Td>
                        </Tr>
                        <Tr>
                          <Td>Goal Tree Size</Td>
                          <Td>{data.tree_state.goal_tree_size}</Td>
                        </Tr>
                        <Tr>
                          <Td>Max depth</Td>
                          <Td>{data.tree_state.max_depth}</Td>
                        </Tr>
                        <Tr>
                          <Td>Max children count</Td>
                          <Td>{data.tree_state.max_children_count}</Td>
                        </Tr>
                        <Tr>
                          <Td>Active</Td>
                          <Td>{data.tree_state.active ? "Active" : "Not active"}</Td>
                        </Tr>
                        <Tr>
                          <Td>Origin</Td>
                          <Td>{data.tree_state.origin || "null"}</Td>
                        </Tr>
                      </Tbody>
                    </Table>
                  </TableContainer>
                </CardBody>
                <CardBody>
                  <MessageTree tree={data.tree} messageId={data.message?.id} />
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
