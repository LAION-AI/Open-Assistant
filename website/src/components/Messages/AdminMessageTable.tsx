import { Avatar } from "@chakra-ui/avatar";
import { Badge, Flex } from "@chakra-ui/layout";
import { Tooltip } from "@chakra-ui/react";
import { createColumnHelper } from "@tanstack/table-core";
import { formatDistanceToNow, formatISO9075 } from "date-fns";
import { Eye } from "lucide-react";
import NextLink from "next/link";
import { ROUTES } from "src/lib/routes";
import { Message } from "src/types/Conversation";
import { isKnownEmoji } from "src/types/Emoji";
import { StrictOmit } from "ts-essentials";

import { DataTable, DataTableProps } from "../DataTable/DataTable";
import { DataTableAction } from "../DataTable/DataTableAction";
import { MessageEmojiButton } from "./MessageEmojiButton";

const columnHelper = createColumnHelper<Message>();

const columns = [
  columnHelper.accessor("text", {
    cell: ({ getValue, row }) => {
      const limit = 80;
      const text = getValue();
      const renderText = text.length > limit ? `${text.slice(0, limit)}...` : text;
      return (
        <Flex alignItems="center">
          <Avatar
            size="xs"
            mr="2"
            src={`${row.original.is_assistant ? "/images/logos/logo.png" : "/images/temp-avatars/av1.jpg"}`}
          ></Avatar>
          {renderText}
          {row.original.deleted && (
            <Badge colorScheme="red" ml="1">
              Deleted
            </Badge>
          )}
        </Flex>
      );
    },
  }),
  columnHelper.accessor("lang", {
    header: "Language",
    cell: ({ getValue }) => <Badge>{getValue()}</Badge>,
  }),
  columnHelper.accessor("emojis", {
    header: "Reactions",
    cell: ({ getValue, row }) => {
      const emojis = getValue();

      emojis["+1"] = emojis["+1"] || 0;
      emojis["-1"] = emojis["-1"] || 0;

      return (
        <Flex gap="2">
          {Object.entries(emojis)
            .filter(([emoji]) => isKnownEmoji(emoji))
            .sort(([emoji]) => -emoji)
            .map(([emoji, count]) => {
              return (
                <MessageEmojiButton
                  key={emoji}
                  emoji={{ name: emoji, count }}
                  checked={row.original.user_emojis.includes(emoji)}
                  userReacted={false}
                  userIsAuthor={false}
                  sx={{
                    ":disabled": {
                      opacity: 1,
                    },
                  }}
                />
              );
            })}
        </Flex>
      );
    },
  }),
  columnHelper.accessor("created_date", {
    header: "Date",
    cell: ({ getValue }) => {
      return <DateDiff>{getValue()}</DateDiff>;
    },
  }),
  columnHelper.accessor((row) => row.id, {
    header: "Actions",
    cell: ({ getValue }) => (
      <DataTableAction
        as={NextLink}
        href={ROUTES.ADMIN_MESSAGE_DETAIL(getValue())}
        icon={Eye}
        aria-label="View message"
      />
    ),
  }),
];
// TODO move this to somewhere
const DateDiff = ({ children }: { children: string | Date | number }) => {
  const date = new Date(children);
  const diff = formatDistanceToNow(date, { addSuffix: true });
  return (
    <Tooltip label={formatISO9075(date)} placement="top">
      {diff}
    </Tooltip>
  );
};

export const AdminMessageTable = (props: StrictOmit<DataTableProps<Message>, "columns">) => {
  return <DataTable columns={columns} {...props}></DataTable>;
};
