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
  Tbody,
  Td,
  Th,
  Thead,
  Tr,
  useDisclosure,
} from "@chakra-ui/react";
import { ColumnDef, flexRender, getCoreRowModel, useReactTable } from "@tanstack/react-table";
import { Filter } from "lucide-react";
import { ChangeEvent, ReactNode } from "react";
import { useDebouncedCallback } from "use-debounce";

export type DataTableColumnDef<T> = ColumnDef<T> & {
  filterable?: boolean;
};

// TODO: stricter type
export type FilterItem = {
  id: string;
  value: string;
};

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
}: DataTableProps<T>) => {
  const { getHeaderGroups, getRowModel } = useReactTable<T>({
    data,
    columns,
    getCoreRowModel: getCoreRowModel(),
  });

  const handleFilterChange = (value: FilterItem) => {
    const idx = filterValues.findIndex((oldValue) => oldValue.id === value.id);
    let newValues: FilterItem[] = [];
    if (idx === -1) {
      newValues = [...filterValues, value];
    } else {
      newValues = filterValues.map((oldValue) => (oldValue.id === value.id ? value : oldValue));
    }
    onFilterChange(newValues);
  };
  return (
    <>
      {!disablePagination && (
        <Flex mb="2">
          <Button onClick={onPreviousClick} disabled={disablePrevious}>
            Previous
          </Button>
          <Spacer />
          <Button onClick={onNextClick} disabled={disableNext}>
            Next
          </Button>
        </Flex>
      )}
      <TableContainer>
        <Table variant="simple">
          <TableCaption>{caption}</TableCaption>
          <Thead>
            {getHeaderGroups().map((headerGroup) => (
              <Tr key={headerGroup.id}>
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
            {getRowModel().rows.map((row) => (
              <Tr key={row.id}>
                {row.getVisibleCells().map((cell) => (
                  <Td key={cell.id}>{flexRender(cell.column.columnDef.cell, cell.getContext())}</Td>
                ))}
              </Tr>
            ))}
          </Tbody>
        </Table>
      </TableContainer>
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

  const handleInputChange = useDebouncedCallback((e: ChangeEvent<HTMLInputElement>) => {
    onChange(e.target.value);
  }, 500);

  return (
    <Popover isOpen={isOpen} onOpen={onOpen} onClose={onClose}>
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
            <Input onChange={handleInputChange} defaultValue={value}></Input>
          </FormControl>
        </PopoverBody>
      </PopoverContent>
    </Popover>
  );
};
