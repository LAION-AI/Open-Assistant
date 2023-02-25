import { useCallback } from "react";
import { del } from "src/lib/api";
import { mutate } from "swr";
import useSWRMutation from "swr/mutation";

export const useAdminDeleteMessageTrigger = () => {
  const { trigger } = useSWRMutation("/api/admin/messages", (path, args: { arg: string }) =>
    del(`/api/admin/delete_message/${args.arg}`)
  );
  const deleteMessage = useCallback(
    (message_id: string) => {
      return trigger(message_id).then(() => {
        mutate(
          (key) =>
            typeof key === "string" && (key.startsWith("/api/messages") || key.startsWith("/api/admin/user_messages")),
          undefined,
          { revalidate: true }
        );
      });
    },
    [trigger]
  );
  return deleteMessage;
};
