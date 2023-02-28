import {
  Box,
  Button,
  Flex,
  FormControl,
  FormLabel,
  Input,
  Popover,
  PopoverArrow,
  PopoverBody,
  PopoverCloseButton,
  PopoverContent,
  PopoverTrigger,
  Spacer,
  Table,
  TableCaption,
  TableContainer,
  TableRowProps,
  Tbody,
  Td,
  Th,
  Thead,
  Tr,
  useDisclosure,
} from "@chakra-ui/react";
import {
  Cell,
  ColumnDef,
  ExpandedState,
  flexRender,
  getCoreRowModel,
  getExpandedRowModel,
  Row,
  useReactTable,
} from "@tanstack/react-table";
import { Filter } from "lucide-react";
import { useTranslation } from "next-i18next";
import { ChangeEvent, ReactNode, useRef, useState } from "react";
import { useDebouncedCallback } from "use-debounce";

// eslint-disable-next-line @typescript-eslint/no-explicit-any
export type DataTableColumnDef<T> = ColumnDef<T, any> & {
  filterable?: boolean;
  span?: number | ((cell: Cell<T, unknown>) => number | undefined);
};

// TODO: stricter type
export type FilterItem = {
  id: string;
  value: string;
};

export type DataTableRowPropsCallback<T> = (row: Row<T>) => TableRowProps;

export type DataTableProps<T> = {
  data: T[];
  columns: DataTableColumnDef<T>[];
  caption?: string;
  filterValues?: FilterItem[];
  onNextClick?: () => void;
  onPreviousClick?: () => void;
  onFilterChange?: (items: FilterItem[]) => void;
  disableNext?: boolean;
  disablePrevious?: boolean;
  disablePagination?: boolean;
  rowProps?: TableRowProps | DataTableRowPropsCallback<T>;
  getSubRows?: (row: T) => T[] | undefined;
};

export const DataTable = <T,>({
  data,
  columns,
  caption,
  filterValues = [],
  onNextClick,
  onPreviousClick,
  onFilterChange,
  disableNext,
  disablePrevious,
  disablePagination,
  rowProps,
  getSubRows,
}: DataTableProps<T>) => {
  const { t } = useTranslation("leaderboard");
  const [expanded, setExpanded] = useState<ExpandedState>({});

  const { getHeaderGroups, getRowModel } = useReactTable<T>({
    data,
    columns,
    getCoreRowModel: getCoreRowModel(),
    getExpandedRowModel: getExpandedRowModel(),
    state: {
      expanded,
    },
    getSubRows,
    onExpandedChange: setExpanded,
  });

  const handleFilterChange = (value: FilterItem) => {
    const idx = filterValues.findIndex((oldValue) => oldValue.id === value.id);
    let newValues: FilterItem[] = [];
    if (idx === -1) {
      newValues = [...filterValues, value];
    } else {
      newValues = filterValues.map((oldValue) => (oldValue.id === value.id ? value : oldValue));
    }
    onFilterChange && onFilterChange(newValues);
  };
  return (
    <>
      {!disablePagination && (
        <Flex mb="2">
          <Button onClick={onPreviousClick} isDisabled={disablePrevious}>
            {t("previous")}
          </Button>
          <Spacer />
          <Button onClick={onNextClick} isDisabled={disableNext}>
            {t("next")}
          </Button>
        </Flex>
      )}
      <TableContainer>
        <Table variant="simple">
          <TableCaption pb={0}>{caption}</TableCaption>
          <Thead>
            {getHeaderGroups().map((headerGroup) => (
              <Tr key={headerGroup.id} whiteSpace="normal">
                {headerGroup.headers.map((header) => (
                  <Th key={header.id}>
                    <Box display="flex" alignItems="center">
                      {header.isPlaceholder ? null : flexRender(header.column.columnDef.header, header.getContext())}
                      {(header.column.columnDef as DataTableColumnDef<T>).filterable && (
                        <FilterModal
                          value={filterValues.find((value) => value.id === header.id)?.value ?? ""}
                          onChange={(value) => handleFilterChange({ id: header.id, value })}
                          label={flexRender(header.column.columnDef.header, header.getContext())}
                        ></FilterModal>
                      )}
                    </Box>
                  </Th>
                ))}
              </Tr>
            ))}
          </Thead>
          <Tbody>
            {getRowModel().rows.map((row) => {
              const props = typeof rowProps === "function" ? rowProps(row) : rowProps;
              return (
                <Tr key={row.id} {...props}>
                  <DataTableRow row={row}></DataTableRow>
                </Tr>
              );
            })}
          </Tbody>
        </Table>
      </TableContainer>
    </>
  );
};

type WithSpanCell<T> = Cell<T, unknown> & { span?: number };

const DataTableRow = <T,>({ row }: { row: Row<T> }) => {
  const cells: WithSpanCell<T>[] = row.getVisibleCells();
  const renderCells: WithSpanCell<T>[] = [];

  for (let i = 0; i < cells.length; i++) {
    const cell = cells[i];
    const span = (cell.column.columnDef as DataTableColumnDef<T>).span;
    const spanValue = typeof span === "function" ? span(cell) : span;
    if (spanValue && spanValue > 1) {
      i += spanValue - 1; // skip next `spanValue - 1` cell
    }
    cell.span = spanValue;
    renderCells.push(cell);
  }

  return (
    <>
      {renderCells.map((cell) => {
        return (
          <Td key={cell.id} colSpan={cell.span}>
            {flexRender(cell.column.columnDef.cell, cell.getContext())}
          </Td>
        );
      })}
    </>
  );
};

const FilterModal = ({
  label,
  onChange,
  value,
}: {
  label: ReactNode;
  onChange: (val: string) => void;
  value: string;
}) => {
  const { isOpen, onOpen, onClose } = useDisclosure();
  const initialFocusRef = useRef();
  const handleInputChange = useDebouncedCallback((e: ChangeEvent<HTMLInputElement>) => {
    onChange(e.target.value);
  }, 500);

  return (
    <Popover isOpen={isOpen} onOpen={onOpen} initialFocusRef={initialFocusRef} onClose={onClose}>
      <PopoverTrigger>
        <Button variant={"unstyled"} ml="2">
          <Filter size="1em"></Filter>
        </Button>
      </PopoverTrigger>
      <PopoverContent w="fit-content">
        <PopoverArrow />
        <PopoverCloseButton />
        <PopoverBody mt="4">
          <FormControl>
            <FormLabel>{label}</FormLabel>
            <Input ref={initialFocusRef} onChange={handleInputChange} autoFocus defaultValue={value}></Input>
          </FormControl>
        </PopoverBody>
      </PopoverContent>
    </Popover>
  );
};
