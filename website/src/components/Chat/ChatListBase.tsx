import "simplebar-react/dist/simplebar.min.css";

import { Button, Card, CardProps } from "@chakra-ui/react";
import { Plus } from "lucide-react";
import Link from "next/link";
import { useTranslation } from "next-i18next";
import { memo } from "react";
import SimpleBar from "simplebar-react";
import { get } from "src/lib/api";
import { API_ROUTES } from "src/lib/routes";
import { GetChatsResponse } from "src/types/Chat";
import useSWR from "swr";

import { HEADER_HEIGHT } from "../Header/Header";
import { ChatListItem } from "./ChatListItem";

export const ChatListBase = memo(function ChatListBase(props: CardProps) {
  const { data: chats } = useSWR<GetChatsResponse>(API_ROUTES.LIST_CHAT, get, {
    revalidateOnFocus: true,
  });
  const { t } = useTranslation(["common", "chat"]);

  return (
    <Card
      w="260px"
      py="3"
      gap="1"
      height={`calc(100vh - ${HEADER_HEIGHT} - ${1.5 * 2}rem)`}
      position="fixed"
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
      {...props}
    >
      <Button
        py="5"
        leftIcon={<Plus size="16px"></Plus>}
        variant="outline"
        justifyContent="start"
        colorScheme="blue"
        borderRadius="lg"
        mx="3"
        mb="2"
        as={Link}
        href="/chat"
      >
        {t("create_chat")}
      </Button>
      <SimpleBar
        style={{ maxHeight: "100%" }}
        classNames={{
          contentEl: "space-y-2 mx-3",
        }}
      >
        {chats?.chats.map((chat) => (
          <ChatListItem key={chat.id} chat={chat}></ChatListItem>
        ))}
      </SimpleBar>
    </Card>
  );
});
