import { Box, Button, CircularProgress, Flex, Input, Tooltip, useBoolean, useOutsideClick } from "@chakra-ui/react";
import { Check, LucideIcon, Pencil, EyeOff, X } from "lucide-react";
import Link from "next/link";
import { useRouter } from "next/router";
import { useTranslation } from "next-i18next";
import { KeyboardEvent, MouseEvent, useCallback, useRef } from "react";
import { del, put } from "src/lib/api";
import { API_ROUTES, ROUTES } from "src/lib/routes";
import { ChatItem } from "src/types/Chat";
import useSWRMutation from "swr/mutation";

export const ChatListItem = ({
  chat,
  onUpdateTitle,
  onHide,
}: {
  chat: ChatItem;
  onUpdateTitle: (params: { chatId: string; title: string }) => void;
  onHide: (params: { chatId: string }) => void;
}) => {
  const { query } = useRouter();
  const { t } = useTranslation("chat");
  const isActive = chat.id === query.id;
  const [isEditing, setIsEditing] = useBoolean(false);
  const inputRef = useRef<HTMLInputElement>(null);
  const rootRef = useRef<HTMLDivElement>(null);
  useOutsideClick({
    ref: rootRef,
    handler: () => {
      if (isEditing) {
        setIsEditing.off();
      }
    },
  });
  const { trigger: updateChatTitle, isMutating: isUpdatingTitle } = useSWRMutation(
    API_ROUTES.UPDATE_CHAT(chat.id),
    put
  );
  const handleConfirmEdit = useCallback(async () => {
    const title = inputRef.current?.value.trim();
    if (!title) return;
    await updateChatTitle({ chat_id: chat.id, title });
    setIsEditing.off();
    onUpdateTitle({ chatId: chat.id, title });
  }, [chat.id, onUpdateTitle, setIsEditing, updateChatTitle]);

  const handleKeyDown = useCallback(
    (e: KeyboardEvent) => {
      if (e.key === "Escape") {
        setIsEditing.off();
      }
      if (e.key === "Enter") {
        handleConfirmEdit();
      }
    },
    [handleConfirmEdit, setIsEditing]
  );

  return (
    <Button
      // @ts-expect-error error due to dynamicly changing as prop
      ref={rootRef}
      {...(!isEditing ? { as: Link, href: ROUTES.CHAT(chat.id) } : { as: "div" })}
      variant={isActive ? "solid" : "ghost"}
      justifyContent="start"
      py="2"
      px={isEditing ? "0" : undefined}
      display="flex"
      w="full"
      fontWeight="normal"
      position="relative"
      role="group"
      borderRadius="lg"
      bg={isEditing ? "transparent" : undefined}
      _hover={{
        bg: isEditing ? "transparent" : undefined,
      }}
    >
      {!isEditing ? (
        <Box
          _groupHover={{ me: "32px" }}
          overflow="hidden"
          me={isActive ? "32px" : undefined}
          textOverflow="clip"
          as="span"
        >
          {chat.title ?? t("empty")}
        </Box>
      ) : (
        <>
          <Input
            ref={inputRef}
            defaultValue={chat.title}
            onKeyDown={handleKeyDown}
            pe="50px"
            borderRadius="lg"
            maxLength={100}
          ></Input>
          <Flex
            position="absolute"
            alignContent="center"
            style={{
              insetInlineEnd: `8px`,
            }}
            gap="1.5"
            zIndex={10}
          >
            {!isUpdatingTitle ? (
              <>
                <ChatListItemIconButton icon={Check} onClick={handleConfirmEdit} />
                <ChatListItemIconButton icon={X} onClick={setIsEditing.off} />
              </>
            ) : (
              <CircularProgress isIndeterminate size="16px"></CircularProgress>
            )}
          </Flex>
        </>
      )}
      <Flex
        display={isActive ? "flex" : "none"}
        _groupHover={{ display: "flex" }}
        position="absolute"
        alignContent="center"
        style={{
          insetInlineEnd: `8px`,
        }}
        gap="1.5"
        zIndex={1}
      >
        {!isEditing && (
          <>
            <EditChatButton onClick={setIsEditing.on} />
            <HideChatButton chatId={chat.id} onHide={onHide} />
          </>
        )}
      </Flex>
    </Button>
  );
};

const EditChatButton = ({ onClick }: { onClick: () => void }) => {
  const { t } = useTranslation("common");

  return <ChatListItemIconButton label={t("edit")} icon={Pencil} onClick={onClick}></ChatListItemIconButton>;
};

const HideChatButton = ({ chatId, onHide }: { chatId: string; onHide?: (params: { chatId: string }) => void }) => {
  const { trigger: triggerHide } = useSWRMutation(API_ROUTES.UPDATE_CHAT(chatId), put);

  const onClick = useCallback(async () => {
    await triggerHide({ chat_id: chatId, hidden: true });
    onHide?.({ chatId });
  }, [onHide, triggerHide, chatId]);

  const { t } = useTranslation("common");

  return <ChatListItemIconButton label={t("hide")} icon={EyeOff} onClick={onClick} />;
};

type ChatListItemIconButtonProps = {
  onClick: () => void;
  label?: string;
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
