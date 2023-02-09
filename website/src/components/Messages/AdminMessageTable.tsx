import { createColumnHelper } from "@tanstack/table-core";
import { Message } from "src/types/Conversation";

import { DataTable } from "../DataTable/DataTable";

const columnHelper = createColumnHelper<Message>();
const columns = [
  columnHelper.accessor("text", {
    cell: ({ getValue }) => {
      const text = getValue();
      return text.length > 100 ? `${text.slice(0, 100)}...` : text;
    },
  }),
  columnHelper.accessor("emojis", {
    header: "Reactions",
  }),
];
export const AdminMessageTable = ({ messages }: { messages: Message[] }) => {
  return <DataTable columns={columns} data={messages}></DataTable>;
};
