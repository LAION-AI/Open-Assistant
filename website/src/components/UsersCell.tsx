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
  useToast,
} from "@chakra-ui/react";
import Link from "next/link";
import { useState } from "react";
import { get } from "src/lib/api";
import type { User } from "src/types/Users";
import useSWR from "swr";

interface Pagination {
  /**
   * The user's `display_name` used for pagination.
   */
  cursor: string;

  /**
   * The pagination direction.
   */
  direction: "forward" | "back";
}

/**
 * Fetches users from the users api route and then presents them in a simple Chakra table.
 */
const UsersCell = () => {
  const toast = useToast();
  const [pagination, setPagination] = useState<Pagination>({ cursor: "", direction: "forward" });
  const [users, setUsers] = useState<User[]>([]);

  // Fetch and save the users.
  // This follows useSWR's recommendation for simple pagination:
  //   https://swr.vercel.app/docs/pagination#when-to-use-useswr
  useSWR(`/api/admin/users?direction=${pagination.direction}&cursor=${pagination.cursor}`, get, {
    onSuccess: (data) => {
      // When no more users can be found, trigger a toast to indicate why no
      // changes have taken place.  We have to maintain a non-empty set of
      // users otherwise we can't paginate using a cursor (since we've lost the
      // cursor).
      if (data.length === 0) {
        toast({
          title: "No more users",
          status: "warning",
          duration: 1000,
          isClosable: true,
        });
        return;
      }
      setUsers(data);
    },
  });

  const toPreviousPage = () => {
    if (users.length >= 0) {
      setPagination({
        cursor: users[0].display_name,
        direction: "back",
      });
    } else {
      toast({
        title: "Can not paginate when no users are found",
        status: "warning",
        duration: 1000,
        isClosable: true,
      });
    }
  };

  const toNextPage = () => {
    if (users.length >= 0) {
      setPagination({
        cursor: users[users.length - 1].display_name,
        direction: "forward",
      });
    } else {
      toast({
        title: "Can not paginate when no users are found",
        status: "warning",
        duration: 1000,
        isClosable: true,
      });
    }
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
