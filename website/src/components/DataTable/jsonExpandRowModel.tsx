import { Card, CardBody, Flex } from "@chakra-ui/react";
import { Cell, CellContext } from "@tanstack/react-table";
import { ChevronDown, ChevronRight } from "lucide-react";

interface ExpandableRow {
  shouldExpand?: boolean;
}

export const createJsonExpandRowModel = <
  T,
  U extends Omit<T, "shouldExpand"> & ExpandableRow = Omit<T, "shouldExpand"> & ExpandableRow
>() => {
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const renderCell = ({ row, getValue }: CellContext<U, any>) => {
    if (!row.original.shouldExpand) {
      // eslint-disable-next-line @typescript-eslint/no-unused-vars
      const { shouldExpand, ...res } = row.original;
      return (
        <Card variant="json">
          <CardBody>
            <pre>{JSON.stringify(res, null, 2)}</pre>
          </CardBody>
        </Card>
      );
    }

    return (
      <Flex alignItems="center">
        {row.getCanExpand() ? (
          <button
            {...{
              onClick: row.getToggleExpandedHandler(),
              style: { cursor: "pointer" },
            }}
          >
            {row.getIsExpanded() ? <ChevronDown /> : <ChevronRight />}
          </button>
        ) : null}{" "}
        {getValue()}
      </Flex>
    );
  };

  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const span = (cell: Cell<U, any>) => (cell.row.original.shouldExpand ? undefined : cell.row.getVisibleCells().length);

  const getSubRows = (row: U) =>
    row.shouldExpand
      ? [
          {
            ...row,
            shouldExpand: false,
          },
        ]
      : undefined;

  const toExpandable = function (arr: T[] | undefined, val = true): U[] {
    // TODO remove `any` workaround
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    return !arr ? [] : (arr.map((element) => ({ ...element, shouldExpand: val })) as any);
  };

  return { renderCell, span, getSubRows, toExpandable };
};
