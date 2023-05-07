import "simplebar-react/dist/simplebar.min.css";

import { Box, CardProps, Flex } from "@chakra-ui/react";
import { Plus } from "lucide-react";
import { useTranslation } from "next-i18next";
import { memo, useCallback } from "react";
import SimpleBar from "simplebar-react";
import { useBoolean } from "usehooks-ts";

import { ChatHiddenSwitch } from "./ChatHiddenSwitch";
import { ChatListItem } from "./ChatListItem";
import { CreateChatButton } from "./CreateChatButton";
import { InferencePoweredBy } from "./InferencePoweredBy";
import { useListChatPagination } from "./useListChatPagination";

export const ChatListBase = memo(function ChatListBase({
  allowHiddenChats,
  ...props
}: CardProps & { allowHiddenChats?: boolean }) {
  const { value: includeHidden, setValue: setIncludeHidden } = useBoolean(false);
  const { loadMoreRef, responses, mutateChatResponses } = useListChatPagination(includeHidden);
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
      <Flex>
        <CreateChatButton
          py="5"
          leftIcon={<Plus size="16px" />}
          variant="outline"
          justifyContent="start"
          colorScheme="blue"
          borderRadius="lg"
          mx="3"
          onUpdated={handleCreateChat}
          flexGrow="1"
        >
          {t("create_chat")}
        </CreateChatButton>
        {allowHiddenChats && <ChatHiddenSwitch onChange={setIncludeHidden} value={includeHidden} />}
      </Flex>
      <SimpleBar
        style={{ padding: "4px 0", maxHeight: "100%", height: "100%", minHeight: "0" }}
        classNames={{
          contentEl: "space-y-2 mx-3 flex flex-col overflow-y-auto",
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
