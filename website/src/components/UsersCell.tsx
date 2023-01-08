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
import fetcher from "src/lib/fetcher";
import useSWR from "swr";

/**
 * Fetches users from the users api route and then presents them in a simple Chakra table.
 */
const UsersCell = () => {
  const [pageIndex, setPageIndex] = useState(0);
  const [users, setUsers] = useState([]);

  // Fetch and save the users.
  // This follows useSWR's recommendation for simple pagination:
  //   https://swr.vercel.app/docs/pagination#when-to-use-useswr
  useSWR(`/api/admin/users?pageIndex=${pageIndex}`, fetcher, {
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
              <Th>Email</Th>
              <Th>Name</Th>
              <Th>Role</Th>
              <Th>Update</Th>
            </Tr>
          </Thead>
          <Tbody>
            {users.map((user, index) => (
              <Tr key={index}>
                <Td>{user.id}</Td>
                <Td>{user.email}</Td>
                <Td>{user.name}</Td>
                <Td>{user.role}</Td>
                <Td>
                  <Link href={`/admin/manage_user/${user.id}`}>Manage</Link>
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
