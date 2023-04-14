import "simplebar-react/dist/simplebar.min.css";

import { Card, CardProps } from "@chakra-ui/react";
import { Plus } from "lucide-react";
import { useTranslation } from "next-i18next";
import { memo, useCallback, useMemo } from "react";
import SimpleBar from "simplebar-react";
import { get } from "src/lib/api";
import { API_ROUTES } from "src/lib/routes";
import { GetChatsResponse } from "src/types/Chat";
import useSWR from "swr";

import { HEADER_HEIGHT } from "../Header/Header";
import { ChatListItem } from "./ChatListItem";
import { CreateChatButton } from "./CreateChatButton";

export const ChatListBase = memo(function ChatListBase({
  isSideBar,
  chats,
  ...props
}: CardProps & { isSideBar: boolean; chats?: GetChatsResponse }) {
  const { data: response, mutate: mutateChatResponse } = useSWR<GetChatsResponse>(
    chats ? null : API_ROUTES.LIST_CHAT,
    get,
    {
      fallbackData: chats,
    }
  );
  const { t } = useTranslation(["common", "chat"]);

  const sideProps: CardProps = useMemo(
    () =>
      isSideBar
        ? {
            w: "260px",
            position: "fixed",
          }
        : {},
    [isSideBar]
  );

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
    <Card
      py="3"
      gap="1"
      height={`calc(100vh - ${HEADER_HEIGHT} - ${1.5 * 2}rem)`}
      overflowY="hidden"
      _light={{
        ".simplebar-scrollbar::before": {
          bg: "gray.300",
        },
      }}
      _dark={{
        ".simplebar-scrollbar::before": {
          bg: "gray.500",
        },
      }}
      {...sideProps}
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
        style={{ maxHeight: "100%", padding: "2px 0" }}
        classNames={{
          contentEl: "space-y-2 mx-3",
        }}
      >
        {response?.chats.map((chat) => (
          <ChatListItem key={chat.id} chat={chat} onUpdateTitle={handleUpdateTitle} onHide={handleHide}></ChatListItem>
        ))}
      </SimpleBar>
    </Card>
  );
});
