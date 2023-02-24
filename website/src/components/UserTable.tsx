import { Card, CardBody, IconButton } from "@chakra-ui/react";
import { createColumnHelper } from "@tanstack/react-table";
import { Pencil } from "lucide-react";
import Link from "next/link";
import { memo, useState } from "react";
import { get } from "src/lib/api";
import type { FetchUsersResponse, User } from "src/types/Users";
import useSWR from "swr";

import { DataTable, DataTableColumnDef, FilterItem } from "./DataTable/DataTable";
import { useCursorPagination } from "./DataTable/useCursorPagination";

const columnHelper = createColumnHelper<User>();

const columns: DataTableColumnDef<User>[] = [
  columnHelper.accessor("user_id", {
    header: "ID",
  }),
  {
    ...columnHelper.accessor("id", {
      header: "Auth ID",
    }),
    filterable: true,
  },
  columnHelper.accessor("auth_method", {
    header: "Auth Method",
  }),
  {
    ...columnHelper.accessor("display_name", {
      header: "Name",
    }),
    filterable: true,
  },
  columnHelper.accessor("role", {
    header: "Role",
  }),
  columnHelper.accessor((user) => user.user_id, {
    cell: ({ getValue }) => (
      <IconButton
        as={Link}
        href={`/admin/manage_user/${getValue()}`}
        aria-label="Manage"
        icon={<Pencil size="1em"></Pencil>}
      ></IconButton>
    ),
    header: "Update",
  }),
];

export const UserTable = memo(function UserTable() {
  const { pagination, resetCursor, toNextPage, toPreviousPage } = useCursorPagination();
  const [filterValues, setFilterValues] = useState<FilterItem[]>([]);

  const handleFilterValuesChange = (values: FilterItem[]) => {
    const last = values.pop();
    if (last) {
      setFilterValues([last]);
    }
    resetCursor();
  };

  // Fetch and save the users.
  // This follows useSWR's recommendation for simple pagination:
  //   https://swr.vercel.app/docs/pagination#when-to-use-useswr

  const filterValue = filterValues.find((value) => value.id === filterValues[filterValues.length - 1]?.id)?.value ?? "";
  const { data, error } = useSWR<FetchUsersResponse<User>>(
    `/api/admin/users?direction=${pagination.direction}&cursor=${
      pagination.cursor
    }&searchDisplayName=${filterValue}&sortKey=${
      filterValues[filterValues.length - 1]?.id === "id"
        ? "username"
        : filterValues[filterValues.length - 1]?.id || "display_name"
    }`,
    get,
    {
      keepPreviousData: true,
    }
  );

  return (
    <Card>
      <CardBody>
        <DataTable
          data={data?.items || []}
          columns={columns}
          caption="Users"
          onNextClick={() => toNextPage(data)}
          onPreviousClick={() => toPreviousPage(data)}
          disableNext={!data?.next}
          disablePrevious={!data?.prev}
          filterValues={filterValues}
          onFilterChange={handleFilterValuesChange}
        ></DataTable>
        {error && "Unable to load users."}
      </CardBody>
    </Card>
  );
});
