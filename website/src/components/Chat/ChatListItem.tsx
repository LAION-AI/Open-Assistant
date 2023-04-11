import { Box, Button, Flex, Tooltip, useToast } from "@chakra-ui/react";
import { LucideIcon, Pencil, Trash2 } from "lucide-react";
import Link from "next/link";
import { useRouter } from "next/router";
import { useTranslation } from "next-i18next";
import { MouseEvent, useCallback } from "react";
import { del } from "src/lib/api";
import { ROUTES } from "src/lib/routes";
import { ChatItem } from "src/types/Chat";
import useSWRMutation from "swr/mutation";

export const ChatListItem = ({ chat }: { chat: ChatItem }) => {
  const { query } = useRouter();
  const { t } = useTranslation("chat");
  const isActive = chat.id === query.id;
  return (
    <Button
      as={Link}
      href={ROUTES.CHAT(chat.id)}
      variant={isActive ? "solid" : "ghost"}
      justifyContent="start"
      py="2"
      display="flex"
      w="full"
      fontWeight="normal"
      position="relative"
      role="group"
      borderRadius="lg"
    >
      <Box
        _groupHover={{ me: "32px" }}
        overflow="hidden"
        me={isActive ? "32px" : undefined}
        textOverflow="clip"
        as="span"
      >
        {chat.title ?? t("empty")}
      </Box>
      <Flex
        display={isActive ? "flex" : "none"}
        _groupHover={{ display: "flex" }}
        position="absolute"
        alignContent="center"
        style={{
          insetInlineEnd: `8px`,
        }}
        gap="1.5"
      >
        <EditChatButton chatId={chat.id}></EditChatButton>
        <DeleteChatButton chatId={chat.id}></DeleteChatButton>
      </Flex>
    </Button>
  );
};

const EditChatButton = ({ chatId }: { chatId: string }) => {
  const { t } = useTranslation("common");
  const toast = useToast();
  return (
    <ChatListItemIconButton
      label={t("edit")}
      icon={Pencil}
      onClick={() => {
        toast({
          title: "Not implemented yet",
        });
      }}
    ></ChatListItemIconButton>
  );
};

const DeleteChatButton = ({ chatId, onDelete }: { chatId: string; onDelete?: () => unknown }) => {
  const { trigger: triggerDelete } = useSWRMutation(`/api/chat?chat_id=${chatId}`, del);

  const onClick = useCallback(async () => {
    await triggerDelete();
    onDelete?.();
  }, [onDelete, triggerDelete]);

  const { t } = useTranslation("common");

  return <ChatListItemIconButton label={t("delete")} icon={Trash2} onClick={onClick} />;
};

type ChatListItemIconButtonProps = {
  onClick: () => void;
  label: string;
  icon: LucideIcon;
};

const ChatListItemIconButton = ({ label, onClick, icon }: ChatListItemIconButtonProps) => {
  return (
    <Tooltip label={label}>
      <Box
        as="button"
        aria-label={label}
        onClick={(e: MouseEvent) => {
          e.stopPropagation();
          e.preventDefault();
          onClick();
        }}
      >
        <Box
          as={icon}
          size="16px"
          color="gray.500"
          _hover={{ color: "gray.700" }}
          _dark={{
            color: "gray.400",
            _hover: {
              color: "white",
            },
          }}
        ></Box>
      </Box>
    </Tooltip>
  );
};
