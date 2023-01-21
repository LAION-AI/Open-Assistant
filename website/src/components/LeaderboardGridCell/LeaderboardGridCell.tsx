import { Table, TableContainer, Tbody, Td, Text, Th, Thead, Tr, useColorModeValue } from "@chakra-ui/react";
import { useTranslation } from "next-i18next";
import React, { useMemo } from "react";
import { useTable } from "react-table";
import { get } from "src/lib/api";
import { LeaderboardReply, LeaderboardTimeFrame } from "src/types/Leaderboard";
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
  const { t } = useTranslation();
  const { data: reply } = useSWRImmutable<LeaderboardReply>(`/api/leaderboard?time_frame=${timeFrame}`, get, {
    revalidateOnMount: true,
  });

  const { getTableProps, getTableBodyProps, headerGroups, rows, prepareRow } = useTable({
    columns,
    data: reply?.leaderboard ?? [],
  });

  const backgroundColor = useColorModeValue("white", "gray.800");

  const lastUpdated = useMemo(() => {
    const val = new Date(reply?.last_updated);
    return t("last_updated_at", { val, formatParams: { val: { dateStyle: "full", timeStyle: "short" } } });
  }, [t, reply?.last_updated]);

  if (!reply) {
    return null;
  }

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
      <Text p="2">{lastUpdated}</Text>
    </TableContainer>
  );
};

export { LeaderboardGridCell };
