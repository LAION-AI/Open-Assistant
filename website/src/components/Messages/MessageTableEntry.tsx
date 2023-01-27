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
import { ClipboardList, Flag, MessageSquare, MoreHorizontal } from "lucide-react";
import { useRouter } from "next/router";
import { useCallback, useEffect, useMemo, useState } from "react";
import { LabelMessagePopup } from "src/components/Messages/LabelPopup";
import { getEmojiIcon, MessageEmojiButton } from "src/components/Messages/MessageEmojiButton";
import { ReportPopup } from "src/components/Messages/ReportPopup";
import { post } from "src/lib/api";
import { Message, MessageEmojis } from "src/types/Conversation";
import { colors } from "styles/Theme/colors";
import useSWRMutation from "swr/mutation";

interface MessageTableEntryProps {
  message: Message;
  enabled?: boolean;
  highlight?: boolean;
}

export function MessageTableEntry({ message, enabled, highlight }: MessageTableEntryProps) {
  const router = useRouter();
  const [emojis, setEmojis] = useState<MessageEmojis>({ emojis: {}, user_emojis: [] });
  useEffect(() => {
    setEmojis({ emojis: message.emojis, user_emojis: message.user_emojis });
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
  const highlightColor = useColorModeValue(colors.light.highlight, colors.dark.highlight);

  const { trigger: sendEmojiChange } = useSWRMutation(`/api/messages/${message.id}/emoji`, post, {
    onSuccess(data) {
      const { emojis, user_emojis } = data;
      setEmojis({ emojis, user_emojis });
    },
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
          {Object.entries(emojis.emojis).map(([emoji, count]) => (
            <MessageEmojiButton
              key={emoji}
              emoji={{ name: emoji, count }}
              checked={emojis.user_emojis.includes(emoji)}
              onClick={() => react(emoji, !emojis.user_emojis.includes(emoji))}
            />
          ))}
          <MessageActions
            react={react}
            userEmoji={emojis.user_emojis}
            onLabel={showLabelPopup}
            onReport={showReportPopup}
            messageId={message.id}
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

  return (
    <MenuItem onClick={() => react(emoji, !checked)} justifyContent="center" color={checked ? activeColor : undefined}>
      {getEmojiIcon(emoji, "NORMAL")}
    </MenuItem>
  );
};

const MessageActions = ({
  react,
  userEmoji,
  onLabel,
  onReport,
  messageId,
}: {
  react: (emoji: string, state: boolean) => void;
  userEmoji: string[];
  onLabel: () => void;
  onReport: () => void;
  messageId: string;
}) => {
  return (
    <Menu>
      <MenuButton>
        <MoreHorizontal />
      </MenuButton>
      <MenuList>
        <MenuGroup title="Reactions">
          <SimpleGrid columns={4}>
            {["+1", "-1"].map((emoji) => (
              <EmojiMenuItem key={emoji} emoji={emoji} checked={userEmoji.includes(emoji)} react={react} />
            ))}
          </SimpleGrid>
        </MenuGroup>
        <MenuDivider />
        <MenuItem onClick={onLabel} icon={<ClipboardList />}>
          Label
        </MenuItem>
        <MenuItem onClick={onReport} icon={<Flag />}>
          Report
        </MenuItem>
        <MenuDivider />
        <MenuItem as="a" href={`/messages/${messageId}`} target="_blank" icon={<MessageSquare />}>
          Open in new tab
        </MenuItem>
      </MenuList>
    </Menu>
  );
};
