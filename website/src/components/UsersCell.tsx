import {
  Button,
  Flex,
  Spacer,
  Stack,
  Table,
  TableCaption,
  TableContainer,
  Tbody,
  Td,
  Th,
  Thead,
  Tr,
} from "@chakra-ui/react";
import Link from "next/link";
import { useState } from "react";
import { get } from "src/lib/api";
import type { User } from "src/types/Users";
import useSWR from "swr";

/**
 * Fetches users from the users api route and then presents them in a simple Chakra table.
 */
const UsersCell = () => {
  const [pageIndex, setPageIndex] = useState(0);
  const [users, setUsers] = useState<User[]>([]);

  // Fetch and save the users.
  // This follows useSWR's recommendation for simple pagination:
  //   https://swr.vercel.app/docs/pagination#when-to-use-useswr
  useSWR(`/api/admin/users?pageIndex=${pageIndex}`, get, {
    onSuccess: setUsers,
  });

  const toPreviousPage = () => {
    setPageIndex(Math.max(0, pageIndex - 1));
  };

  const toNextPage = () => {
    setPageIndex(pageIndex + 1);
  };

  // Present users in a naive table.
  return (
    <Stack>
      <Flex p="2">
        <Button onClick={toPreviousPage}>Previous</Button>
        <Spacer />
        <Button onClick={toNextPage}>Next</Button>
      </Flex>
      <TableContainer>
        <Table variant="simple">
          <TableCaption>Users</TableCaption>
          <Thead>
            <Tr>
              <Th>Id</Th>
              <Th>Auth Id</Th>
              <Th>Auth Method</Th>
              <Th>Name</Th>
              <Th>Role</Th>
              <Th>Update</Th>
            </Tr>
          </Thead>
          <Tbody>
            {users.map(({ id, user_id, auth_method, display_name, role }) => (
              <Tr key={user_id}>
                <Td>{user_id}</Td>
                <Td>{id}</Td>
                <Td>{auth_method}</Td>
                <Td>{display_name}</Td>
                <Td>{role}</Td>
                <Td>
                  <Link href={`/admin/manage_user/${user_id}`}>Manage</Link>
                </Td>
              </Tr>
            ))}
          </Tbody>
        </Table>
      </TableContainer>
    </Stack>
  );
};

export default UsersCell;
