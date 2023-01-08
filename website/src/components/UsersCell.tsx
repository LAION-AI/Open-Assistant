import { Table, TableCaption, TableContainer, Tbody, Td, Th, Thead, Tr } from "@chakra-ui/react";
import Link from "next/link";
import { useState } from "react";
import fetcher from "src/lib/fetcher";
import useSWR from "swr";

/**
 * Fetches users from the users api route and then presents them in a simple Chakra table.
 */
const UsersCell = () => {
  // Fetch and save the users.
  const [users, setUsers] = useState([]);
  const { isLoading } = useSWR("/api/admin/users", fetcher, {
    onSuccess: setUsers,
  });

  // Present users in a naive table.
  return (
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
  );
};

export default UsersCell;
