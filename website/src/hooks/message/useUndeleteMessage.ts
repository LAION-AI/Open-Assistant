import { put } from "src/lib/api";
import { API_ROUTES } from "src/lib/routes";
import { mutate } from "swr";
import useSWRMutation from "swr/mutation";

export const useUndeleteMessage = (messageId: string, onSuccess?: () => void) => {
  return useSWRMutation(API_ROUTES.ADMIN_UNDELETE_MESSAGE(messageId), put, {
    onSuccess: async () => {
      onSuccess?.();
      await mutate(
        (key) =>
          typeof key === "string" && (key.startsWith("/api/messages") || key.startsWith("/api/admin/user_messages")),
        undefined,
        { revalidate: true }
      );
    },
  });
};
