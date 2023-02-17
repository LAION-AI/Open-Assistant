import { Table, TableContainer, Tbody, Td, Th, Thead, Tr } from "@chakra-ui/react";

interface TableProps {
  headers: string[];
  rows: string[][];
}
// Create a SimpleTable component that takes in a list of headers and a list of rows
export const SimpleTable = ({ headers, rows }: TableProps) => {
  return (
    <TableContainer>
      <Table>
        <Thead>
          <Tr>
            {headers.map((header) => (
              <Th key={header}>
                {header.split(" ").map((word, index) => (
                  <div key={header + index}>
                    {word}
                    <br />
                  </div>
                ))}
              </Th>
            ))}
          </Tr>
        </Thead>
        <Tbody>
          {rows.map((row) => (
            <Tr key={row[0]}>
              {row.map((cell, index) => (
                <Td key={row[0] + index}>{cell}</Td>
              ))}
            </Tr>
          ))}
        </Tbody>
      </Table>
    </TableContainer>
  );
};
