import { Badge, Flex, Stack, Tooltip } from "@chakra-ui/react";
import { boolean } from "boolean";
import { User } from "lucide-react";
import { useRouter } from "next/router";
import { useTranslation } from "next-i18next";
import { ROUTES } from "src/lib/routes";
import { Message, MessageRevision } from "src/types/Conversation";

import { BaseMessageEntry } from "./BaseMessageEntry";
import { MessageCreateDate } from "./MessageCreateDate";
import { BaseMessageEmojiButton } from "./MessageEmojiButton";
import { MessageInlineEmojiRow } from "./MessageInlineEmojiRow";

export interface MessageHistoryTableProps {
  message: Message;
  revisions: MessageRevision[];
}

export function MessageHistoryTable({ message, revisions }: MessageHistoryTableProps) {
  const { t } = useTranslation(["message"]);
  const router = useRouter();

  return (
    <Stack spacing={4}>
      {(revisions.length === 0
        ? ([
            {
              text: message.text,
              created_date: message.created_date,
              user_id: message.user_id,
              user_is_author: message.user_is_author,
            },
          ] as Omit<MessageRevision, "id" | "message_id">[])
        : (revisions.map((revision) => ({
            text: revision.text,
            created_date: revision.created_date,
            user_id: revision.user_id,
            user_is_author: revision.user_is_author,
          })) as Omit<MessageRevision, "id" | "message_id">[])
      ).map(({ text, created_date, user_id, user_is_author }, index, array) => (
        <BaseMessageEntry
          key={`version-${index}`}
          content={text}
          avatarProps={{
            name: `${boolean(message.is_assistant) ? "Assistant" : "User"}`,
            src: `${boolean(message.is_assistant) ? "/images/logos/logo.png" : "/images/temp-avatars/av1.jpg"}`,
          }}
          highlight={index === array.length - 1}
        >
          <Flex justifyContent={"space-between"} marginTop={2} alignItems={"center"}>
            <MessageCreateDate date={created_date} />
            <MessageInlineEmojiRow>
              <BaseMessageEmojiButton
                emoji={User}
                label="Manage User"
                onClick={() => router.push(ROUTES.ADMIN_USER_DETAIL(user_id))}
              />
            </MessageInlineEmojiRow>
          </Flex>
          <Flex
            position={"absolute"}
            gap="2"
            top="-2.5"
            style={{
              insetInlineEnd: "1.25rem",
            }}
          >
            {index === 0 && (
              <Tooltip label={"This is the original version of this message"} placement="top">
                <Badge colorScheme={"blue"}>Original</Badge>
              </Tooltip>
            )}
            {user_is_author && (
              <Tooltip label={t("message_author_explain")} placement="top">
                <Badge size="sm" colorScheme="green" textTransform="capitalize">
                  {t("message_author")}
                </Badge>
              </Tooltip>
            )}
          </Flex>
        </BaseMessageEntry>
      ))}
    </Stack>
  );
}
