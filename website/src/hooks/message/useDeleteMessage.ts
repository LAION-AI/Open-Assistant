import { del } from "src/lib/api";
import { API_ROUTES } from "src/lib/routes";
import { mutate } from "swr";
import useSWRMutation from "swr/mutation";

export const useDeleteMessage = (messageId: string, onSuccess?: () => void) => {
  return useSWRMutation(API_ROUTES.ADMIN_DELETE_MESSAGE(messageId), del, {
    onSuccess: async () => {
      onSuccess?.();
      await mutate(
        (key) => typeof key === "string" && (key.startsWith("/api/messages") || key.startsWith("/api/admin/messages")),
        undefined,
        { revalidate: true }
      );
    },
  });
};
