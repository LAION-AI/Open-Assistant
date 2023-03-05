import { Avatar } from "@chakra-ui/avatar";
import { Badge, Flex } from "@chakra-ui/layout";
import {
  Button,
  HStack,
  Modal,
  ModalBody,
  ModalCloseButton,
  ModalContent,
  ModalFooter,
  ModalHeader,
  ModalOverlay,
  Tooltip,
  useDisclosure,
} from "@chakra-ui/react";
import { createColumnHelper } from "@tanstack/table-core";
import { formatDistanceToNow, formatISO9075 } from "date-fns";
import { Eye, Trash } from "lucide-react";
import NextLink from "next/link";
import { useMemo, useState } from "react";
import { useTranslation } from "react-i18next";
import { useDeleteMessage } from "src/hooks/message/useDeleteMessage";
import { ROUTES } from "src/lib/routes";
import { Message } from "src/types/Conversation";
import { isKnownEmoji } from "src/types/Emoji";
import { StrictOmit } from "ts-essentials";

import { DataTable, DataTableProps } from "../DataTable/DataTable";
import { DataTableAction } from "../DataTable/DataTableAction";
import { MessageEmojiButton } from "./MessageEmojiButton";

const columnHelper = createColumnHelper<Message>();

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
  const [deleteMessageId, setDeleteMessageId] = useState<string | null>(null);
  // eslint-disable-next-line @typescript-eslint/no-non-null-assertion
  const { isMutating, trigger } = useDeleteMessage(deleteMessageId!);

  const { isOpen, onOpen, onClose } = useDisclosure();

  const columns = useMemo(() => {
    return [
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
                <Badge colorScheme="red" ml="1" textTransform="capitalize">
                  Deleted
                </Badge>
              )}
              {row.original.review_result === false && (
                <Badge colorScheme="yellow" textTransform="capitalize">
                  Spam
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
        cell: ({ getValue, row }) => {
          const id = getValue();
          return (
            <HStack spacing="2">
              <DataTableAction
                as={NextLink}
                href={ROUTES.ADMIN_MESSAGE_DETAIL(id)}
                icon={Eye}
                aria-label="View message"
              />
              {!row.original.deleted && (
                <DataTableAction
                  onClick={() => {
                    setDeleteMessageId(id);
                    onOpen();
                  }}
                  icon={Trash}
                  aria-label="Delete message"
                  isLoading={isMutating && deleteMessageId === id}
                />
              )}
            </HStack>
          );
        },
      }),
    ];
  }, [deleteMessageId, isMutating, onOpen]);

  const { t } = useTranslation(["common", "message"]);

  return (
    <>
      <Modal isOpen={isOpen} onClose={onClose} isCentered>
        <ModalOverlay />
        <ModalContent>
          <ModalHeader>Confirm deleting this message</ModalHeader>
          <ModalCloseButton />
          <ModalBody>
            <div>Delete this message?</div>
          </ModalBody>
          <ModalFooter>
            <Button variant="ghost" mr={3} onClick={onClose}>
              {t("cancel")}
            </Button>
            <Button
              colorScheme="blue"
              onClick={() => {
                onClose();
                trigger();
              }}
            >
              {t("confirm")}
            </Button>
          </ModalFooter>
        </ModalContent>
      </Modal>
      <DataTable columns={columns} {...props}></DataTable>
    </>
  );
};
