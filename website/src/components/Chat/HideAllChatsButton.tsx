import {
  AlertDialog,
  AlertDialogBody,
  AlertDialogContent,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogOverlay,
  Button,
  IconButton,
  Tooltip,
  useDisclosure,
  useToast,
} from "@chakra-ui/react";
import { EyeOff } from "lucide-react";
import { useTranslation } from "next-i18next";
import { useCallback, useRef, useState } from "react";
import { API_ROUTES } from "src/lib/routes";
import useSWRMutation from "swr/mutation";
import { put } from "src/lib/api";

interface HideAllChatsButtonProps {
  chatIds: string[];
  onHideAll: () => void;
}

export const HideAllChatsButton = ({ chatIds, onHideAll }: HideAllChatsButtonProps) => {
  const { t } = useTranslation(["chat", "common"]);
  const { isOpen, onOpen, onClose } = useDisclosure();
  const cancelRef = useRef<HTMLButtonElement>(null);
  const toast = useToast();
  const [isHiding, setIsHiding] = useState(false);

  const { trigger: triggerHide } = useSWRMutation(API_ROUTES.UPDATE_CHAT(), put);

  const handleHideAll = useCallback(async () => {
    if (chatIds.length === 0) {
      onClose();
      return;
    }

    setIsHiding(true);
    try {
      // Hide all chats sequentially
      for (const chatId of chatIds) {
        await triggerHide({ chat_id: chatId, hidden: true });
      }
      
      toast({
        title: t("chat:hide_all_success"),
        status: "success",
        duration: 3000,
        isClosable: true,
      });
      
      onHideAll();
      onClose();
    } catch (error) {
      toast({
        title: t("chat:hide_all_error"),
        status: "error",
        duration: 3000,
        isClosable: true,
      });
    } finally {
      setIsHiding(false);
    }
  }, [chatIds, onHideAll, onClose, toast, t, triggerHide]);

  if (chatIds.length === 0) {
    return null;
  }

  return (
    <>
      <Tooltip label={t("chat:hide_all_chats")}>
        <IconButton
          icon={<EyeOff size="16px" />}
          aria-label={t("chat:hide_all_chats")}
          onClick={onOpen}
          variant="ghost"
          size="sm"
        />
      </Tooltip>

      <AlertDialog isOpen={isOpen} leastDestructiveRef={cancelRef} onClose={onClose}>
        <AlertDialogOverlay>
          <AlertDialogContent>
            <AlertDialogHeader fontSize="lg" fontWeight="bold">
              {t("chat:hide_all_chats")}
            </AlertDialogHeader>

            <AlertDialogBody>
              {t("chat:hide_all_confirmation", { count: chatIds.length })}
            </AlertDialogBody>

            <AlertDialogFooter>
              <Button ref={cancelRef} onClick={onClose} isDisabled={isHiding}>
                {t("common:cancel")}
              </Button>
              <Button
                colorScheme="blue"
                onClick={handleHideAll}
                ml={3}
                isLoading={isHiding}
                loadingText={t("chat:hiding")}
              >
                {t("common:confirm")}
              </Button>
            </AlertDialogFooter>
          </AlertDialogContent>
        </AlertDialogOverlay>
      </AlertDialog>
    </>
  );
};
