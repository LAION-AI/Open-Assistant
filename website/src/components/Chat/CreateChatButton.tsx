import { Button, ButtonProps } from "@chakra-ui/react";
import { useRouter } from "next/router";
import { useCallback } from "react";
import { post } from "src/lib/api";
import { API_ROUTES } from "src/lib/routes";
import useSWRMutation from "swr/mutation";

export const useCreateChat = () => {
  const router = useRouter();
  const { trigger: newChatTrigger } = useSWRMutation<{ id: string }>(API_ROUTES.LIST_CHAT, post);
  const createChat = useCallback(async () => {
    const { id } = await newChatTrigger();
    router.push(`/chat/${id}`);
    return id;
  }, [newChatTrigger, router]);
  return createChat;
};

interface CreateChatButtonProps extends ButtonProps {
  onUpdated: () => void;
}

export const CreateChatButton = ({ children, onUpdated, ...props }: CreateChatButtonProps) => {
  const createChat = useCreateChat();
  return (
    <Button
      onClick={async () => {
        await createChat();
        onUpdated();
      }}
      {...props}
    >
      {children}
    </Button>
  );
};
