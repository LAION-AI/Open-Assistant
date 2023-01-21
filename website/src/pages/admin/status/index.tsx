import {
  Box,
  Card,
  Button,
  CircularProgress,
  Container,
  SimpleGrid,
  Text,
  Table,
  TableCaption,
  TableContainer,
  Tbody,
  Td,
  Th,
  Thead,
  Tr,
  View,
  useColorMode,
  useToast,
} from "@chakra-ui/react";
import Head from "next/head";
import { useRouter } from "next/router";
import { useSession } from "next-auth/react";
import { useEffect, useState } from "react";
import useSWRImmutable from "swr/immutable";
import { getAdminLayout } from "src/components/Layout";
import poster from "src/lib/poster";
import prisma from "src/lib/prismadb";
import { get } from "src/lib/api";

/**
 * Provides the admin status page that shows result of calls to several backend API endpoints,
 * namely /api/v1/tasks/availability, /api/v1/stats/, /api/v1/stats/tree_manager
 */

const StatusIndex = ({ user }) => {
  const toast = useToast();
  const router = useRouter();
  const { data: session, status } = useSession();

  const { colorMode } = useColorMode();
  const backgroundColor = colorMode === "light" ? "white" : "gray.700";
  const dataBackgroundColor = colorMode === "light" ? "gray.100" : "gray.800";
  // Check when the user session is loaded and re-route if the user is not an
  // admin.  This follows the suggestion by NextJS for handling private pages:
  //   https://nextjs.org/docs/api-reference/next/router#usage
  //
  // All admin pages should use the same check and routing steps.
  useEffect(() => {
    if (status === "loading") {
      return;
    }
    if (session?.user?.role === "admin") {
      return;
    }
    router.push("/");
  }, [router, session, status]);

  const {
    data: dataStatus,
    error: errorStatus,
    isLoading: isLoadingStatus,
  } = useSWRImmutable("/api/admin/status", get);

  const { tasksAvailability, stats, treeManager } = dataStatus || {};

  return (
    <>
      <Head>
        <title>Status - Open Assistant</title>
        <meta
          name="description"
          content="Conversational AI for everyone. An open source project to create a chat enabled GPT LLM run by LAION and contributors around the world."
        />
      </Head>

      <SimpleGrid columns={[1, 1, 1, 1, 1, 2]} gap={4}>
        <Card>
          <CardBody>
            <Text as="h1" fontSize="3xl" textAlign="center">
              /api/v1/tasks/availability
            </Text>
            <Box bg={dataBackgroundColor} borderRadius="xl" p="6" pt="4" pr="12">
              <pre id="json">
                {tasksAvailability ? JSON.stringify(tasksAvailability, null, 2) : <CircularProgress isIndeterminate />}
              </pre>
            </Box>
          </CardBody>
        </Card>

        <Card bg={backgroundColor} p="6" pt="4" pr="6">
          <Text as="h1" fontSize="3xl" textAlign="center">
            /api/v1/stats/
          </Text>
          <Box bg={dataBackgroundColor} borderRadius="xl" p="6" pt="4" pr="12">
            <pre id="json">{stats ? JSON.stringify(stats, null, 2) : <CircularProgress isIndeterminate />}</pre>
          </Box>
        </Card>
      </SimpleGrid>
      <br />
      <Card bg={backgroundColor} p="6" pt="4" pr="6">
        <Text as="h1" fontSize="3xl" textAlign="center">
          /api/v1/stats/tree_manager
        </Text>

        {treeManager ? (
          <Box>
            <Text as="h2" fontSize="2xl">
              state_counts
            </Text>
            <Box bg={dataBackgroundColor} borderRadius="xl" p="6" pt="4" pr="12">
              <pre id="json">{JSON.stringify(treeManager.state_counts, null, 2)}</pre>
            </Box>
            <TableContainer>
              <br />
              <Text as="h2" fontSize="2xl">
                message_counts
              </Text>
              <Table variant="simple">
                <TableCaption>Tree Manager</TableCaption>
                <Thead>
                  <Tr>
                    <Th>Message Tree ID</Th>
                    <Th>State</Th>
                    <Th>Depth</Th>
                    <Th>Oldest</Th>
                    <Th>Youngest</Th>
                    <Th>Count</Th>
                    <Th>Goal Tree Size</Th>
                  </Tr>
                </Thead>
                <Tbody>
                  {treeManager.message_counts.map(
                    ({ message_tree_id, state, depth, oldest, youngest, count, goal_tree_size }) => (
                      <Tr key={message_tree_id}>
                        <Td>{message_tree_id}</Td>
                        <Td>{state}</Td>
                        <Td>{depth}</Td>
                        <Td>{oldest}</Td>
                        <Td>{youngest}</Td>
                        <Td>{count}</Td>
                        <Td>{goal_tree_size}</Td>
                      </Tr>
                    )
                  )}
                </Tbody>
              </Table>
            </TableContainer>
          </Box>
        ) : (
          <CircularProgress isIndeterminate />
        )}
      </Card>
    </>
  );
};

StatusIndex.getLayout = getAdminLayout;

export default StatusIndex;
