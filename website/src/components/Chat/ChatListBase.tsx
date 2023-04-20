import "simplebar-react/dist/simplebar.min.css";

import { Box, CardProps } from "@chakra-ui/react";
import { Plus } from "lucide-react";
import { useTranslation } from "next-i18next";
import { memo, useCallback } from "react";
import SimpleBar from "simplebar-react";
import { get } from "src/lib/api";
import { API_ROUTES } from "src/lib/routes";
import { GetChatsResponse } from "src/types/Chat";
import useSWR from "swr";

import { ChatListItem } from "./ChatListItem";
import { CreateChatButton } from "./CreateChatButton";
import { InferencePoweredBy } from "./InferencePoweredBy";

export const ChatListBase = memo(function ChatListBase({
  chats, // TODO: can we remove this?
  ...props
}: CardProps & { chats?: GetChatsResponse }) {
  const { data: response, mutate: mutateChatResponse } = useSWR<GetChatsResponse>(API_ROUTES.LIST_CHAT, get, {
    fallbackData: chats,
  });
  const { t } = useTranslation(["common", "chat"]);

  const handleUpdateTitle = useCallback(
    ({ chatId, title }: { chatId: string; title: string }) => {
      mutateChatResponse(
        (chatResponse) => ({
          ...chatResponse,
          chats: chatResponse?.chats.map((chat) => (chat.id === chatId ? { ...chat, title } : chat)) || [],
        }),
        false
      );
    },
    [mutateChatResponse]
  );

  const handleHide = useCallback(
    ({ chatId }: { chatId: string }) => {
      mutateChatResponse(
        (chatResponse) => ({
          ...chatResponse,
          chats: chatResponse?.chats.filter((chat) => chat.id !== chatId) || [],
        }),
        false
      );
    },
    [mutateChatResponse]
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
      <CreateChatButton
        py="5"
        leftIcon={<Plus size="16px"></Plus>}
        variant="outline"
        justifyContent="start"
        colorScheme="blue"
        borderRadius="lg"
        mx="3"
        mb="2"
      >
        {t("create_chat")}
      </CreateChatButton>
      <SimpleBar
        style={{ padding: "4px 0", maxHeight: "100%", height: "100%", minHeight: "0" }}
        classNames={{
          contentEl: "space-y-2 mx-3 flex flex-col overflow-y-auto",
        }}
      >
        {response?.chats.map((chat) => (
          <ChatListItem key={chat.id} chat={chat} onUpdateTitle={handleUpdateTitle} onHide={handleHide}></ChatListItem>
        ))}
      </SimpleBar>
      <InferencePoweredBy />
    </Box>
  );
});
