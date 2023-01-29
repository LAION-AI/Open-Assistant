import { Card, CardBody, IconButton } from "@chakra-ui/react";
import { createColumnHelper } from "@tanstack/react-table";
import { Pencil } from "lucide-react";
import Link from "next/link";
import { memo, useState } from "react";
import { get } from "src/lib/api";
import type { FetchUsersResponse, User } from "src/types/Users";
import useSWR from "swr";

import { DataTable, DataTableColumnDef, FilterItem } from "./DataTable";

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

const columnHelper = createColumnHelper<User>();

const columns: DataTableColumnDef<User>[] = [
  columnHelper.accessor("user_id", {
    header: "ID",
  }),
  columnHelper.accessor("id", {
    header: "Auth ID",
  }),
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
  const [pagination, setPagination] = useState<Pagination>({ cursor: "", direction: "forward" });
  const [filterValues, setFilterValues] = useState<FilterItem[]>([]);
  const handleFilterValuesChange = (values: FilterItem[]) => {
    setFilterValues(values);
    setPagination((old) => ({ ...old, cursor: "" }));
  };
  // Fetch and save the users.
  // This follows useSWR's recommendation for simple pagination:
  //   https://swr.vercel.app/docs/pagination#when-to-use-useswr
  const display_name = filterValues.find((value) => value.id === "display_name")?.value ?? "";
  const { data, error } = useSWR<FetchUsersResponse<User>>(
    `/api/admin/users?direction=${pagination.direction}&cursor=${pagination.cursor}&searchDisplayName=${display_name}&sortKey=display_name`,
    get,
    {
      keepPreviousData: true,
    }
  );

  const toPreviousPage = () => {
    setPagination({
      cursor: data.prev,
      direction: "back",
    });
  };

  const toNextPage = () => {
    setPagination({
      cursor: data.next,
      direction: "forward",
    });
  };

  return (
    <Card>
      <CardBody>
        <DataTable
          data={data?.items || []}
          columns={columns}
          caption="Users"
          onNextClick={toNextPage}
          onPreviousClick={toPreviousPage}
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
