import "simplebar-react/dist/simplebar.min.css";

import { Box, Button, CardProps, Flex } from "@chakra-ui/react";
import { EyeOff, Plus } from "lucide-react";
import { useTranslation } from "next-i18next";
import { memo, useCallback, useState } from "react";
import SimpleBar from "simplebar-react";

import { ChatListItem } from "./ChatListItem";
import { ChatViewSelection } from "./ChatViewSelection";
import { CreateChatButton } from "./CreateChatButton";
import { InferencePoweredBy } from "./InferencePoweredBy";
import { ChatListViewSelection, useListChatPagination } from "./useListChatPagination";
import useSWRMutation from "swr/mutation";
import { API_ROUTES } from "src/lib/routes";
import { put } from "src/lib/api";

export const ChatListBase = memo(function ChatListBase({
  allowViews,
  noScrollbar,
  ...props
}: CardProps & { allowViews?: boolean; noScrollbar?: boolean }) {
  const [view, setView] = useState<ChatListViewSelection>("visible");
  const { loadMoreRef, responses, mutateChatResponses } = useListChatPagination(view);
  const chats = responses?.flatMap((response) => response.chats) || [];

  const { t } = useTranslation(["common", "chat"]);

  const { trigger: triggerHideAll, isMutating: isHidingAll } = useSWRMutation(
    API_ROUTES.UPDATE_CHAT(),
    put
  );

  const handleHideAllChats = useCallback(async () => {
    // Hide all visible chats
    const hidePromises = chats.map((chat) =>
      triggerHideAll({ chat_id: chat.id, hidden: true })
    );
    await Promise.all(hidePromises);
    // Refresh the list
    mutateChatResponses();
  }, [chats, triggerHideAll, mutateChatResponses]);

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

  const content = (
    <>
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
    </>
  );

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
      {chats.length > 0 && view === "visible" && (
        <Flex px="2" pb="2">
          <Button
            leftIcon={<EyeOff size="16px" />}
            variant="ghost"
            size="sm"
            onClick={handleHideAllChats}
            isLoading={isHidingAll}
            colorScheme="gray"
          >
            {t("chat:hide_all_chats")}
          </Button>
        </Flex>
      )}
      {noScrollbar ? (
        content
      ) : (
        <SimpleBar
          style={{ padding: "8px", height: "100%", minHeight: "150px" }}
          classNames={{
            contentEl: "flex flex-col items-center overflow-y-hidden min-h-full",
          }}
        >
          {content}
        </SimpleBar>
      )}
      <InferencePoweredBy />
    </Box>
  );
});
