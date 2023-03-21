import { Avatar, Badge, Box, Flex } from "@chakra-ui/react";
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
import { Eye, RotateCw, Trash } from "lucide-react";
import NextLink from "next/link";
import { useTranslation } from "next-i18next";
import { useMemo, useState } from "react";
import { useCallback } from "react";
import { useDeleteMessage } from "src/hooks/message/useDeleteMessage";
import { get } from "src/lib/api";
import { API_ROUTES, ROUTES } from "src/lib/routes";
import { FetchMessagesCursorResponse, Message } from "src/types/Conversation";
import { isKnownEmoji } from "src/types/Emoji";
import useSWRImmutable from "swr/immutable";

import { useUndeleteMessage } from "../../hooks/message/useUndeleteMessage";
import { DataTable, DataTableRowPropsCallback } from "../DataTable/DataTable";
import { DataTableAction } from "../DataTable/DataTableAction";
import { useCursorPagination } from "../DataTable/useCursorPagination";
import { UserDisplayNameCell } from "../UserDisplayNameCell";
import { MessageEmojiButton } from "./MessageEmojiButton";

const columnHelper = createColumnHelper<
  Message & {
    isActive?: boolean;
  }
>();

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

export const AdminMessageTable = ({ userId, includeUser }: { userId?: string; includeUser?: boolean }) => {
  const [deleteMessageId, setDeleteMessageId] = useState<string | null>(null);
  const [undeleteMessageId, setUndeleteMessageId] = useState<string | null>(null);
  const [activeMessageId, setActiveMessageId] = useState<string>();
  const { pagination, toNextPage, toPreviousPage } = useCursorPagination();
  const {
    data: res,
    isLoading,
    mutate: mutateMessageList,
  } = useSWRImmutable<FetchMessagesCursorResponse>(
    API_ROUTES.ADMIN_MESSAGE_LIST({
      cursor: pagination.cursor,
      direction: pagination.direction,
      user_id: userId,
      include_user: includeUser,
    }),
    get,
    {
      keepPreviousData: true,
    }
  );

  const data = useMemo(() => {
    return res?.items.map((m) => ({ ...m, isActive: m.id === activeMessageId })) || [];
  }, [activeMessageId, res?.items]);

  const { isMutating: isDeleteMutating, trigger: deleteTrigger } = useDeleteMessage(
    deleteMessageId!,
    mutateMessageList
  );
  const { isMutating: isUndeleteMutating, trigger: undeleteTrigger } = useUndeleteMessage(
    undeleteMessageId,
    mutateMessageList
  );

  const { isOpen, onOpen, onClose: disclosureClose } = useDisclosure();
  const onClose = () => {
    disclosureClose();
    if (deleteMessageId) setDeleteMessageId(null);
    if (undeleteMessageId) setUndeleteMessageId(null);
  };

  const columns = useMemo(() => {
    return [
      columnHelper.accessor("user", {
        cell({ getValue }) {
          const user = getValue();
          if (!user) {
            return null;
          }
          return (
            <UserDisplayNameCell
              authMethod={user.auth_method}
              displayName={user.display_name}
              userId={user.user_id}
            ></UserDisplayNameCell>
          );
        },
      }),
      columnHelper.accessor("text", {
        cell: ({ getValue, row }) => {
          const limit = 95;
          const text = getValue();
          const isActive = row.original.isActive;
          const renderText = isActive ? text : text.length > limit ? `${text.slice(0, limit)}...` : text;

          return (
            <Box display="-webkit-box" wordBreak="break-all" whiteSpace="pre-wrap" w="md">
              <Avatar
                size="xs"
                mr="2"
                src={`${row.original.is_assistant ? "/images/logos/logo.png" : "/images/temp-avatars/av1.jpg"}`}
              ></Avatar>
              {renderText}
              {!row.original.parent_id && (
                <Badge colorScheme="green" ml="1">
                  Root
                </Badge>
              )}
              {row.original.deleted && (
                <Badge colorScheme="red" ml="1">
                  Deleted
                </Badge>
              )}
              {row.original.review_result === false && <Badge colorScheme="yellow">Spam</Badge>}
            </Box>
          );
        },
      }),

      columnHelper.accessor("lang", {
        header: "Language",
        cell: ({ getValue }) => <Badge textTransform="uppercase">{getValue()}</Badge>,
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
      columnHelper.accessor("review_count", {
        header: "Review Count",
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
              {!row.original.deleted ? (
                <DataTableAction
                  onClick={() => {
                    setDeleteMessageId(id);
                    onOpen();
                  }}
                  icon={Trash}
                  aria-label="Delete message"
                  isLoading={isDeleteMutating && deleteMessageId === id}
                />
              ) : (
                <DataTableAction
                  onClick={() => {
                    setUndeleteMessageId(id);
                    onOpen();
                  }}
                  icon={RotateCw}
                  aria-label="Undelete message"
                  isLoading={isUndeleteMutating && undeleteMessageId === id}
                />
              )}
            </HStack>
          );
        },
      }),
    ];
  }, [deleteMessageId, isDeleteMutating, isUndeleteMutating, onOpen, undeleteMessageId]);

  const { t } = useTranslation(["common", "message"]);
  const rowProps: DataTableRowPropsCallback<Message> = useCallback(
    (row) => {
      return {
        onClick: () => {
          setActiveMessageId(row.original.id);
        },
      };
    },
    [setActiveMessageId]
  );
  const columnVisibility = useMemo(() => ({ user: !!includeUser }), [includeUser]);
  return (
    <>
      <Modal isOpen={isOpen} onClose={onClose} isCentered>
        <ModalOverlay />
        <ModalContent>
          <ModalHeader>Confirm {deleteMessageId ? "deleting" : "undeleting"} this message</ModalHeader>
          <ModalCloseButton />
          <ModalBody>
            <p>
              {undeleteMessageId
                ? "By undeleting this message you take the risk to undelete every parent messages that may also be deleted."
                : ""}
            </p>
            {deleteMessageId ? "Delete" : "Are you sure to undelete"} this message? <p></p>
          </ModalBody>
          <ModalFooter>
            <Button variant="ghost" mr={3} onClick={onClose}>
              {t("cancel")}
            </Button>
            <Button
              colorScheme="blue"
              onClick={async () => {
                if (deleteMessageId) await deleteTrigger();
                else await undeleteTrigger();
                onClose();
              }}
            >
              {t("confirm")}
            </Button>
          </ModalFooter>
        </ModalContent>
      </Modal>
      <DataTable
        columns={columns}
        data={data}
        rowProps={rowProps}
        disableNext={!res?.next}
        disablePrevious={!res?.prev}
        onNextClick={() => toNextPage(res)}
        onPreviousClick={() => toPreviousPage(res)}
        columnVisibility={columnVisibility}
        isLoading={isLoading}
      ></DataTable>
    </>
  );
};
