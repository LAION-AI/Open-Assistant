import { Table, TableContainer, Tbody, Td, Th, Thead, Tr, useColorModeValue } from "@chakra-ui/react";
import React from "react";
import { useTable } from "react-table";
import { get } from "src/lib/api";
import { LeaderboardEntity, LeaderboardTimeFrame } from "src/types/Leaderboard";
import useSWRImmutable from "swr/immutable";

const columns = [
  {
    Header: "Rank",
    accessor: "rank",
    style: { width: "90px" },
  },
  {
    Header: "Score",
    accessor: "leader_score",
    style: { width: "90px" },
  },
  {
    Header: "User",
    accessor: "display_name",
  },
];

/**
 * Presents a grid of leaderboard entries with more detailed information.
 */
const LeaderboardGridCell = ({ timeFrame }: { timeFrame: LeaderboardTimeFrame }) => {
  const { data } = useSWRImmutable<LeaderboardEntity[]>(`/api/leaderboard?time_frame=${timeFrame}`, get, {
    fallbackData: [],
    revalidateOnMount: true,
  });
  const backgroundColor = useColorModeValue("white", "gray.800");

  const { getTableProps, getTableBodyProps, headerGroups, rows, prepareRow } = useTable({ columns, data });

  return (
    <TableContainer>
      <Table {...getTableProps()}>
        <Thead bg={backgroundColor}>
          {headerGroups.map((headerGroup, idx) => (
            <Tr key={idx} {...headerGroup.getHeaderGroupProps()}>
              {headerGroup.headers.map((column) => (
                <Th {...column.getHeaderProps([{ style: column.style }])} key={column.id}>
                  {column.render("Header")}
                </Th>
              ))}
            </Tr>
          ))}
        </Thead>

        <Tbody {...getTableBodyProps()}>
          {rows.map((row) => {
            prepareRow(row);
            return (
              <Tr key={row.id} {...row.getRowProps()}>
                {row.cells.map((cell, idx) => {
                  return (
                    <Td key={row.id + idx} {...cell.getCellProps([{ style: cell.column.style }])}>
                      {cell.render("Cell")}
                    </Td>
                  );
                })}
              </Tr>
            );
          })}
        </Tbody>
      </Table>
    </TableContainer>
  );
};

export { LeaderboardGridCell };
