import { Card, CircularProgress } from "@chakra-ui/react";
import { MessageConversation } from "src/components/Messages/MessageConversation";
import { get } from "src/lib/api";
import useSWR from "swr";

interface UserMessagesCellProps {
  /**
   * The Web API route to fetch user messages from.  By default is
   * `/api/messages/users` and fetches the logged in user's messages.
   */
  path?: string;
}

/**
 * Fetches the messages corresponding to a user and presents them in a table.
 */
const UserMessagesCell = ({ path }: UserMessagesCellProps) => {
  const url = path || "/api/messages/user";
  const { data: messages, isLoading } = useSWR(url, get, {
    refreshInterval: 2000,
    keepPreviousData: true,
  });

  return (
    <Card boxShadow="base" borderRadius="xl" className="p-6 shadow-sm">
      {isLoading ? <CircularProgress isIndeterminate /> : <MessageConversation messages={messages} />}
    </Card>
  );
};

export { UserMessagesCell };
