import React, { useCallback } from "react";
import { Button, ButtonProps } from "@chakra-ui/react";
import useSWRMutation from "swr/mutation";
import { API_ROUTES } from "src/lib/routes";
import { put } from "src/lib/api";
import { useTranslation } from "react-i18next";
import { EyeOff } from "lucide-react";

import { ChatListItemIconButton } from "./ChatListItem";

export const HideAllChatButton = ({
  chatIds,
  onHide,
}: {
  chatIds: string[];
  onHide?: (params: { chatId: string }) => void;
}) => {
  const { trigger: triggerHide } = useSWRMutation(API_ROUTES.UPDATE_CHAT(), put);

  const onClick = useCallback(async () => {
    for (const chatId of chatIds) {
      await triggerHide({ chat_id: chatId, hidden: true });
      onHide?.({ chatId });
    }
  }, [onHide, triggerHide, chatIds]);

  const { t } = useTranslation("common");

  return <ChatListItemIconButton label={t("hide_all")} icon={EyeOff} onClick={onClick} />;
};
