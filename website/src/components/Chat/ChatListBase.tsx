import "simplebar-react/dist/simplebar.min.css";

import { Box, CardProps } from "@chakra-ui/react";
import { Plus } from "lucide-react";
import { useTranslation } from "next-i18next";
import { memo, useCallback } from "react";
import SimpleBar from "simplebar-react";
import { GetChatsResponse } from "src/types/Chat";

import { ChatListItem } from "./ChatListItem";
import { CreateChatButton } from "./CreateChatButton";
import { InferencePoweredBy } from "./InferencePoweredBy";
import { useListChatPagination } from "./useListChatPagination";

export const ChatListBase = memo(function ChatListBase({
  initialChats, // TODO: can we remove this?
  ...props
}: CardProps & { initialChats?: GetChatsResponse }) {
  const { loadMoreRef, responses, mutateChatResponses } = useListChatPagination(initialChats);
  const chats = responses?.flatMap((response) => response.chats) || [];

  const { t } = useTranslation(["common", "chat"]);

  const handleUpdateTitle = useCallback(
    ({ chatId, title }: { chatId: string; title: string }) => {
      mutateChatResponses(
        (chatResponses) => [
          ...(chatResponses?.map((chatResponse) => ({
            ...chatResponse,
            chats: chatResponse.chats.map((chat) => {
              if (chat.id === chatId) {
                return {
                  ...chat,
                  title,
                };
              }
              return chat;
            }),
          })) || []),
        ],
        false
      );
    },
    [mutateChatResponses]
  );

  const handleHide = useCallback(
    ({ chatId }: { chatId: string }) => {
      mutateChatResponses(
        (chatResponses) => [
          ...(chatResponses?.map((chatResponse) => ({
            ...chatResponse,
            chats: chatResponse.chats.filter((chat) => {
              return chat.id !== chatId;
            }),
          })) || []),
        ],
        false
      );
    },
    [mutateChatResponses]
  );

  const handleCreateChat = useCallback(() => {
    mutateChatResponses();
  }, [mutateChatResponses]);

  return (
    <Box
      gap="1"
      height="full"
      minH="0"
      display="flex"
      flexDirection="column"
      bg="whiteAlpha.400"
      _dark={{
        bg: "blackAlpha.400",
      }}
      {...props}
    >
      <CreateChatButton
        py="5"
        leftIcon={<Plus size="16px"></Plus>}
        variant="outline"
        justifyContent="start"
        colorScheme="blue"
        borderRadius="lg"
        mx="3"
        mb="2"
        onUpdated={handleCreateChat}
      >
        {t("create_chat")}
      </CreateChatButton>
      <SimpleBar
        style={{ padding: "4px 0", maxHeight: "100%", height: "100%", minHeight: "0" }}
        classNames={{
          contentEl: "space-y-2 mx-3 flex flex-col overflow-y-auto",
        }}
      >
        {chats.map((chat) => (
          <ChatListItem key={chat.id} chat={chat} onUpdateTitle={handleUpdateTitle} onHide={handleHide} />
        ))}
        <div ref={loadMoreRef} />
      </SimpleBar>
      <InferencePoweredBy />
    </Box>
  );
});
