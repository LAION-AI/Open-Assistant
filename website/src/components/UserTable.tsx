import { IconButton, useToast } from "@chakra-ui/react";
import { createColumnHelper } from "@tanstack/react-table";
import Link from "next/link";
import { memo, useState } from "react";
import { FaPen } from "react-icons/fa";
import { get } from "src/lib/api";
import { FetchUsersResponse } from "src/lib/oasst_api_client";
import type { User } from "src/types/Users";
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
        icon={<FaPen></FaPen>}
      ></IconButton>
    ),
    header: "Update",
  }),
];

export const UserTable = memo(function UserTable() {
  const toast = useToast();
  const [pagination, setPagination] = useState<Pagination>({ cursor: "", direction: "forward" });
  const [response, setResponse] = useState<Omit<FetchUsersResponse<User>, "sort_key" | "order">>({
    items: [],
  });
  const [filterValues, setFilterValues] = useState<FilterItem[]>([]);
  const handleFilterValuesChange = (values: FilterItem[]) => {
    setFilterValues(values);
    setPagination((old) => ({ ...old, cursor: "" }));
  };
  // Fetch and save the users.
  // This follows useSWR's recommendation for simple pagination:
  //   https://swr.vercel.app/docs/pagination#when-to-use-useswr
  const display_name = filterValues.find((value) => value.id === "display_name")?.value ?? "";
  useSWR<
    FetchUsersResponse<User>
  >(`/api/admin/users?direction=${pagination.direction}&cursor=${pagination.cursor}&searchDisplayName=${display_name}&sortKey=display_name`, get, {
    onSuccess: (data) => {
      // When no more users can be found, trigger a toast to indicate why no
      // changes have taken place.  We have to maintain a non-empty set of
      // users otherwise we can't paginate using a cursor (since we've lost the
      // cursor).
      if (data.items.length === 0) {
        toast({
          title: "No more users",
          status: "warning",
          duration: 1000,
          isClosable: true,
        });
        return;
      }
      setResponse(data);
    },
  });

  const toPreviousPage = () => {
    if (response.items.length >= 0) {
      setPagination({
        cursor: response.prev,
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
    if (response.items.length >= 0) {
      setPagination({
        cursor: response.next,
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

  return (
    <DataTable
      data={response.items}
      columns={columns}
      caption="Users"
      onNextClick={toNextPage}
      onPreviousClick={toPreviousPage}
      filterValues={filterValues}
      onFilterChange={handleFilterValuesChange}
    ></DataTable>
  );
});
