import {
  Avatar,
  Box,
  HStack,
  Menu,
  MenuButton,
  MenuDivider,
  MenuGroup,
  MenuItem,
  MenuList,
  SimpleGrid,
  useBreakpointValue,
  useColorModeValue,
  useDisclosure,
} from "@chakra-ui/react";
import { boolean } from "boolean";
import { ClipboardList, Flag, MessageSquare, MoreHorizontal, Trash, User } from "lucide-react";
import { useRouter } from "next/router";
import { useSession } from "next-auth/react";
import { useTranslation } from "next-i18next";
import { useCallback, useEffect, useMemo, useState } from "react";
import { LabelMessagePopup } from "src/components/Messages/LabelPopup";
import { MessageEmojiButton } from "src/components/Messages/MessageEmojiButton";
import { ReportPopup } from "src/components/Messages/ReportPopup";
import { del, post } from "src/lib/api";
import { colors } from "src/styles/Theme/colors";
import { Message, MessageEmojis } from "src/types/Conversation";
import { emojiIcons, isKnownEmoji } from "src/types/Emoji";
import { mutate } from "swr";
import useSWRMutation from "swr/mutation";

interface MessageTableEntryProps {
  message: Message;
  enabled?: boolean;
  highlight?: boolean;
}

export function MessageTableEntry({ message, enabled, highlight }: MessageTableEntryProps) {
  const router = useRouter();
  const [emojiState, setEmojis] = useState<MessageEmojis>({ emojis: {}, user_emojis: [] });
  useEffect(() => {
    setEmojis({
      emojis: message?.emojis || {},
      user_emojis: message?.user_emojis || [],
    });
  }, [message.emojis, message.user_emojis]);

  const goToMessage = useCallback(() => router.push(`/messages/${message.id}`), [router, message.id]);
  const { isOpen: reportPopupOpen, onOpen: showReportPopup, onClose: closeReportPopup } = useDisclosure();
  const { isOpen: labelPopupOpen, onOpen: showLabelPopup, onClose: closeLabelPopup } = useDisclosure();

  const backgroundColor = useColorModeValue("gray.100", "gray.700");
  const backgroundColor2 = useColorModeValue("#DFE8F1", "#42536B");

  const borderColor = useColorModeValue("blackAlpha.200", "whiteAlpha.200");

  const inlineAvatar = useBreakpointValue({ base: true, sm: false });

  const avatar = useMemo(
    () => (
      <Avatar
        borderColor={borderColor}
        size={inlineAvatar ? "xs" : "sm"}
        mr={inlineAvatar ? 2 : 0}
        name={`${boolean(message.is_assistant) ? "Assistant" : "User"}`}
        src={`${boolean(message.is_assistant) ? "/images/logos/logo.png" : "/images/temp-avatars/av1.jpg"}`}
      />
    ),
    [borderColor, inlineAvatar, message.is_assistant]
  );
  const highlightColor = useColorModeValue(colors.light.active, colors.dark.active);

  const { trigger: sendEmojiChange } = useSWRMutation(`/api/messages/${message.id}/emoji`, post, {
    onSuccess: setEmojis,
  });
  const react = (emoji: string, state: boolean) => {
    sendEmojiChange({ op: state ? "add" : "remove", emoji });
  };

  return (
    <HStack w={["full", "full", "full", "fit-content"]} gap={2}>
      {!inlineAvatar && avatar}
      <Box
        width={["full", "full", "full", "fit-content"]}
        maxWidth={["full", "full", "full", "2xl"]}
        p="4"
        borderRadius="md"
        bg={message.is_assistant ? backgroundColor : backgroundColor2}
        outline={highlight && "2px solid black"}
        outlineColor={highlightColor}
        onClick={enabled && goToMessage}
        whiteSpace="pre-wrap"
        cursor={enabled && "pointer"}
        style={{ position: "relative" }}
      >
        {inlineAvatar && avatar}
        {message.text}
        <HStack
          style={{ float: "right", position: "relative", right: "-0.3em", bottom: "-0em", marginLeft: "1em" }}
          onClick={(e) => e.stopPropagation()}
        >
          {Object.entries(emojiState.emojis)
            .filter(([emoji]) => isKnownEmoji(emoji))
            .map(([emoji, count]) => (
              <MessageEmojiButton
                key={emoji}
                emoji={{ name: emoji, count }}
                checked={emojiState.user_emojis.includes(emoji)}
                onClick={() => react(emoji, !emojiState.user_emojis.includes(emoji))}
              />
            ))}
          <MessageActions
            react={react}
            userEmoji={emojiState.user_emojis}
            onLabel={showLabelPopup}
            onReport={showReportPopup}
            message={message}
          />
          <LabelMessagePopup messageId={message.id} show={labelPopupOpen} onClose={closeLabelPopup} />
          <ReportPopup messageId={message.id} show={reportPopupOpen} onClose={closeReportPopup} />
        </HStack>
      </Box>
    </HStack>
  );
}

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
  const EmojiIcon = emojiIcons.get(emoji);
  return (
    <MenuItem onClick={() => react(emoji, !checked)} justifyContent="center" color={checked ? activeColor : undefined}>
      <EmojiIcon />
    </MenuItem>
  );
};

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
  const { t } = useTranslation(["message", "common"]);
  const { trigger } = useSWRMutation(`/api/admin/delete_message/${message.id}`, del);
  const { data } = useSession() || {};
  const role = data?.user?.role;

  const handleDelete = async () => {
    await trigger();
    mutate((key) => typeof key === "string" && key.startsWith("/api/messages"), undefined, { revalidate: true });
  };

  return (
    <Menu>
      <MenuButton>
        <MoreHorizontal />
      </MenuButton>
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
        <MenuItem as="a" href={`/messages/${message.id}`} target="_blank" icon={<MessageSquare />}>
          {t("open_new_tab_action")}
        </MenuItem>
        {role === "admin" && (
          <>
            <MenuDivider />
            <MenuItem as="a" href={`/admin/manage_user/${message.user_id}`} target="_blank" icon={<User />}>
              {t("view_user")}
            </MenuItem>
            <MenuItem onClick={handleDelete} icon={<Trash />}>
              {t("common:delete")}
            </MenuItem>
          </>
        )}
      </MenuList>
    </Menu>
  );
};
