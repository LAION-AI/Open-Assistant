import { Card, CardBody, CardHeader, CircularProgress, Grid, Text, 
    TableContainer, Table, TableCaption, Thead, Tr, Th, Tbody, Td, 
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
  }>(`/api/admin/messages/${messageId}/tree`, get);

  const { data: treeState, isLoading: isLoadingTreeState, error: errorTreeState } = useSWRImmutable<{
    message_tree_id: string;
    state: string;
    active: boolean; 
    goal_tree_size: number; 
    max_children_count: number; 
    max_depth: number;
    origin: string; 
  }>(`/api/admin/messages/${messageId}/tree/state`, get);

  console.log(treeState)

  return (
    <>
      <Head>
        <title>Open Assistant</title>
      </Head>
      <AdminArea>
        {isLoading && isLoadingTreeState && <CircularProgress isIndeterminate></CircularProgress>}
        {error && errorTreeState && "Unable to load message tree"}
        {data && treeState && 
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
                    <Table variant='striped' colorScheme='teal'>
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
                          <Td>{treeState.state}</Td>
                        </Tr>
                        <Tr>
                          <Td>Goal Tree Size</Td>
                          <Td>{treeState.goal_tree_size}</Td>
                        </Tr>
                        <Tr>
                          <Td>Max depth</Td>
                          <Td>{treeState.max_depth}</Td>
                         </Tr>
                        <Tr>
                          <Td>Max children count</Td>
                          <Td>{treeState.max_children_count}</Td>
                        </Tr>
                        <Tr>
                          <Td>Active</Td>
                          <Td>{treeState.active ? "Active": "Not active"}</Td>
                        </Tr>
                        <Tr>  
                          <Td>Origin</Td>
                          <Td>{treeState.origin || "null"}</Td>
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
