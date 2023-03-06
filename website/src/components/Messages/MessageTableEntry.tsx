import {
  Badge,
  Flex,
  Menu,
  MenuButton,
  MenuDivider,
  MenuGroup,
  MenuItem,
  MenuList,
  Portal,
  SimpleGrid,
  Text,
  Tooltip,
  useColorModeValue,
  useDisclosure,
  useToast,
} from "@chakra-ui/react";
import { boolean } from "boolean";
import {
  ClipboardList,
  Copy,
  Flag,
  Link,
  MessageSquare,
  MoreHorizontal,
  Shield,
  Slash,
  Trash,
  User,
} from "lucide-react";
import NextLink from "next/link";
import { useRouter } from "next/router";
import { useTranslation } from "next-i18next";
import { useCallback, useEffect, useState } from "react";
import { forwardRef } from "react";
import { LabelMessagePopup } from "src/components/Messages/LabelPopup";
import { MessageEmojiButton } from "src/components/Messages/MessageEmojiButton";
import { ReportPopup } from "src/components/Messages/ReportPopup";
import { useHasAnyRole } from "src/hooks/auth/useHasAnyRole";
import { useCurrentLocale } from "src/hooks/locale/useCurrentLocale";
import { useDeleteMessage } from "src/hooks/message/useDeleteMessage";
import { post, put } from "src/lib/api";
import { ROUTES } from "src/lib/routes";
import { colors } from "src/styles/Theme/colors";
import { Message, MessageEmojis } from "src/types/Conversation";
import { emojiIcons, isKnownEmoji } from "src/types/Emoji";
import useSWRMutation from "swr/mutation";

import { BaseMessageEntry } from "./BaseMessageEntry";
import { MessageInlineEmojiRow } from "./MessageInlineEmojiRow";

interface MessageTableEntryProps {
  message: Message;
  enabled?: boolean;
  highlight?: boolean;
  showAuthorBadge?: boolean;
  showCreatedDate?: boolean;
}

// eslint-disable-next-line react/display-name
export const MessageTableEntry = forwardRef<HTMLDivElement, MessageTableEntryProps>(
  ({ message, enabled, highlight, showAuthorBadge, showCreatedDate }, ref) => {
    const [emojiState, setEmojis] = useState<MessageEmojis>({ emojis: {}, user_emojis: [] });
    useEffect(() => {
      const emojis = { ...message.emojis };
      emojis["+1"] = emojis["+1"] || 0;
      emojis["-1"] = emojis["-1"] || 0;
      setEmojis({
        emojis: emojis,
        user_emojis: message?.user_emojis || [],
      });
    }, [message.emojis, message.user_emojis]);

    const { isOpen: reportPopupOpen, onOpen: showReportPopup, onClose: closeReportPopup } = useDisclosure();
    const { isOpen: labelPopupOpen, onOpen: showLabelPopup, onClose: closeLabelPopup } = useDisclosure();

    const highlightColor = useColorModeValue(colors.light.active, colors.dark.active);

    const { trigger: sendEmojiChange } = useSWRMutation(`/api/messages/${message.id}/emoji`, post, {
      onSuccess: (data) => {
        data.emojis["+1"] = data.emojis["+1"] || 0;
        data.emojis["-1"] = data.emojis["-1"] || 0;
        setEmojis(data);
      },
    });
    const react = (emoji: string, state: boolean) => {
      sendEmojiChange({ op: state ? "add" : "remove", emoji });
    };

    const isAdminOrMod = useHasAnyRole(["admin", "moderator"]);
    const { t } = useTranslation(["message"]);

    const router = useRouter();

    const handleOnClick = useCallback(() => {
      enabled && router.push(ROUTES.MESSAGE_DETAIL(message.id));
    }, [enabled, message.id, router]);

    return (
      <BaseMessageEntry
        ref={ref}
        content={message.text}
        avatarProps={{
          name: `${boolean(message.is_assistant) ? "Assistant" : "User"}`,
          src: `${boolean(message.is_assistant) ? "/images/logos/logo.png" : "/images/temp-avatars/av1.jpg"}`,
        }}
        outline={highlight ? "2px solid black" : undefined}
        outlineColor={highlightColor}
        cursor={enabled ? "pointer" : undefined}
        overflowX="auto"
        onClick={handleOnClick}
      >
        <Flex justifyContent="space-between" mt="2" alignItems="center">
          {showCreatedDate ? (
            <MessageCreateDate date={message.created_date}></MessageCreateDate>
          ) : (
            // empty span is required to make emoji displayed at the end of row
            <span></span>
          )}
          <MessageInlineEmojiRow>
            <Badge variant="subtle" colorScheme="gray" fontSize="xx-small">
              {message.lang}
            </Badge>
            {Object.entries(emojiState.emojis)
              .filter(([emoji]) => isKnownEmoji(emoji))
              .sort(([emoji]) => -emoji)
              .map(([emoji, count]) => {
                return (
                  <MessageEmojiButton
                    key={emoji}
                    emoji={{ name: emoji, count }}
                    checked={emojiState.user_emojis.includes(emoji)}
                    userReacted={emojiState.user_emojis.length > 0}
                    userIsAuthor={!!message.user_is_author}
                    onClick={() => react(emoji, !emojiState.user_emojis.includes(emoji))}
                  />
                );
              })}
            <MessageActions
              react={react}
              userEmoji={emojiState.user_emojis}
              onLabel={showLabelPopup}
              onReport={showReportPopup}
              message={message}
            />
            <LabelMessagePopup message={message} show={labelPopupOpen} onClose={closeLabelPopup} />
            <ReportPopup messageId={message.id} show={reportPopupOpen} onClose={closeReportPopup} />
          </MessageInlineEmojiRow>
        </Flex>
        <Flex
          position="absolute"
          gap="2"
          top="-2.5"
          style={{
            insetInlineEnd: "1.25rem",
          }}
        >
          {showAuthorBadge && message.user_is_author && (
            <Tooltip label={t("message_author_explain")} placement="top">
              <Badge size="sm" colorScheme="green" textTransform="capitalize">
                {t("message_author")}
              </Badge>
            </Tooltip>
          )}
          {message.deleted && isAdminOrMod && (
            <Badge colorScheme="red" textTransform="capitalize">
              Deleted {/* dont translate, it's admin only feature */}
            </Badge>
          )}
          {message.review_result === false && isAdminOrMod && (
            <Badge colorScheme="yellow" textTransform="capitalize">
              Spam {/* dont translate, it's admin only feature */}
            </Badge>
          )}
        </Flex>
      </BaseMessageEntry>
    );
  }
);

const me = { base: 3, md: 6 };

const MessageCreateDate = ({ date }: { date: string }) => {
  const locale = useCurrentLocale();
  const createdDateColor = useColorModeValue("blackAlpha.600", "gray.400");
  return (
    <Text as="span" fontSize="small" color={createdDateColor} fontWeight="medium" me={me}>
      {new Intl.DateTimeFormat(locale, {
        hour: "2-digit",
        minute: "2-digit",
        year: "numeric",
        month: "2-digit",
        day: "2-digit",
      }).format(new Date(date))}
    </Text>
  );
};

const EmojiMenuItem = ({
  emoji,
  checked,
  react,
}: {
  emoji: string;
  checked?: boolean;
  react: (emoji: string, state: boolean) => void;
}) => {
  const activeColor = useColorModeValue(colors.light.active, colors.dark.active);
  // eslint-disable-next-line @typescript-eslint/no-non-null-assertion
  const EmojiIcon = emojiIcons.get(emoji)!;
  return (
    <MenuItem onClick={() => react(emoji, !checked)} justifyContent="center" color={checked ? activeColor : undefined}>
      <EmojiIcon />
    </MenuItem>
  );
};

const CHAR_COUNT = 10;

const MessageActions = ({
  react,
  userEmoji,
  onLabel,
  onReport,
  message,
}: {
  react: (emoji: string, state: boolean) => void;
  userEmoji: string[];
  onLabel: () => void;
  onReport: () => void;
  message: Message;
}) => {
  const toast = useToast();
  const { t } = useTranslation(["message", "common"]);
  const { id } = message;

  const { trigger: stopTree } = useSWRMutation(`/api/admin/stop_tree/${id}`, put, {
    onSuccess: () => {
      const displayId = id.slice(0, CHAR_COUNT) + "..." + id.slice(-CHAR_COUNT);
      toast({
        title: t("common:success"),
        description: t("tree_stopped", { id: displayId }),
        status: "success",
        duration: 5000,
        isClosable: true,
      });
    },
  });

  const { trigger: handleDelete } = useDeleteMessage(message.id);

  const handleStop = () => {
    stopTree();
  };

  const handleCopy = (text: string) => {
    navigator.clipboard.writeText(text);
    const displayId = text.slice(0, CHAR_COUNT) + "..." + text.slice(-CHAR_COUNT);

    toast({
      title: t("common:copied"),
      description: displayId,
      status: "info",
      duration: 5000,
      isClosable: true,
    });
  };

  const isAdminOrMod = useHasAnyRole(["admin", "moderator"]);
  const { locale } = useRouter();
  return (
    <Menu>
      <MenuButton>
        <MoreHorizontal />
      </MenuButton>
      <Portal>
        <MenuList>
          <MenuGroup title={t("reactions")}>
            <SimpleGrid columns={4}>
              {["+1", "-1"].map((emoji) => (
                <EmojiMenuItem key={emoji} emoji={emoji} checked={userEmoji?.includes(emoji)} react={react} />
              ))}
            </SimpleGrid>
          </MenuGroup>
          <MenuDivider />
          <MenuItem onClick={onLabel} icon={<ClipboardList />}>
            {t("label_action")}
          </MenuItem>
          <MenuItem onClick={onReport} icon={<Flag />}>
            {t("report_action")}
          </MenuItem>
          <MenuDivider />
          <MenuItem as={NextLink} href={`/messages/${id}`} target="_blank" icon={<MessageSquare />}>
            {t("open_new_tab_action")}
          </MenuItem>

          <MenuItem
            onClick={() =>
              handleCopy(
                `${window.location.protocol}//${window.location.host}${
                  locale === "en" ? "" : `/${locale}`
                }/messages/${id}`
              )
            }
            icon={<Link />}
          >
            {t("copy_message_link")}
          </MenuItem>
          <MenuItem onClick={() => handleCopy(message.text)} icon={<Copy />}>
            {t("copy_message_text")}
          </MenuItem>
          {!!isAdminOrMod && (
            <>
              <MenuDivider />
              <MenuItem onClick={() => handleCopy(id)} icon={<Copy />}>
                {t("copy_message_id")}
              </MenuItem>
              <MenuItem as={NextLink} href={ROUTES.ADMIN_MESSAGE_DETAIL(message.id)} target="_blank" icon={<Shield />}>
                View in admin area
              </MenuItem>
              <MenuItem as={NextLink} href={ROUTES.ADMIN_USER_DETAIL(message.user_id)} target="_blank" icon={<User />}>
                {t("view_user")}
              </MenuItem>
              {!message.deleted && (
                <MenuItem onClick={handleDelete} icon={<Trash />}>
                  {t("common:delete")}
                </MenuItem>
              )}
              <MenuItem onClick={handleStop} icon={<Slash />}>
                {t("stop_tree")}
              </MenuItem>
            </>
          )}
        </MenuList>
      </Portal>
    </Menu>
  );
};
