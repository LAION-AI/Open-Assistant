import { IconButton, IconButtonProps } from "@chakra-ui/react";
import { Trash } from "lucide-react";
import { useCallback } from "react";
import { del } from "src/lib/api";
import useSWRMutation from "swr/mutation";

export interface DeleteChatButtonProps extends Omit<IconButtonProps, "aria-label"> {
  chatId: string;
  onDelete?: () => unknown;
}

export const DeleteChatButton = ({ chatId, onDelete, ...props }: DeleteChatButtonProps) => {
  const { trigger: triggerDelete } = useSWRMutation("/api/chat?chat_id=" + chatId, del);

  const onClick = useCallback(async () => {
    await triggerDelete();
    onDelete?.();
  }, [onDelete, triggerDelete]);

  return <IconButton icon={<Trash />} aria-label="delete" onClick={onClick} {...props} />;
};
