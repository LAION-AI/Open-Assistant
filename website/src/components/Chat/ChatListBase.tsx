import "simplebar-react/dist/simplebar.min.css";

import { Box, CardProps, Flex } from "@chakra-ui/react";
import { Plus } from "lucide-react";
import { useTranslation } from "next-i18next";
import { memo, useCallback, useState } from "react";
import SimpleBar from "simplebar-react";

import { ChatListItem } from "./ChatListItem";
import { ChatViewSelection } from "./ChatViewSelection";
import { CreateChatButton } from "./CreateChatButton";
import { InferencePoweredBy } from "./InferencePoweredBy";
import { ChatListViewSelection, useListChatPagination } from "./useListChatPagination";

export const ChatListBase = memo(function ChatListBase({ allowViews, ...props }: CardProps & { allowViews?: boolean }) {
  const [view, setView] = useState<ChatListViewSelection>("visible");
  const { loadMoreRef, responses, mutateChatResponses } = useListChatPagination(view);
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

  const removeItemFromList = useCallback(
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
      <Flex flexDirection={["column", "row"]} alignItems="stretch" p="2" gap="3">
        <CreateChatButton
          leftIcon={<Plus size="16px" />}
          variant="outline"
          justifyContent="start"
          colorScheme="blue"
          borderRadius="lg"
          onUpdated={handleCreateChat}
          flexGrow="1"
        >
          {t("create_chat")}
        </CreateChatButton>
        {allowViews && (
          <ChatViewSelection w={["full", "auto"]} onChange={(e) => setView(e.target.value as ChatListViewSelection)} />
        )}
      </Flex>
      <SimpleBar
        style={{ padding: "8px", maxHeight: "100%", height: "100%", minHeight: "0" }}
        classNames={{
          contentEl: "space-y-2 flex flex-col overflow-y-auto",
        }}
      >
        {chats.map((chat) => (
          <ChatListItem
            key={chat.id}
            chat={chat}
            onUpdateTitle={handleUpdateTitle}
            onHide={removeItemFromList}
            onDelete={removeItemFromList}
          />
        ))}
        <div ref={loadMoreRef} />
      </SimpleBar>
      <InferencePoweredBy />
    </Box>
  );
});
