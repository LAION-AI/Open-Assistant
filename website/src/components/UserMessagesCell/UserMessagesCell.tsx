import { Box, CircularProgress, useColorModeValue } from "@chakra-ui/react";
import { MessageTable } from "src/components/Messages/MessageTable";
import fetcher from "src/lib/fetcher";
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
const UserMessagesCell = ({ path }) => {
  const url = path || "/api/messages/user";
  const { data: messages, isLoading } = useSWR(url, fetcher, {
    refreshInterval: 2000,
  });
  // TODO(#651): This box coloring and styling is used in multiple places.  We
  // should factor it into a common ui component.
  const boxBgColor = useColorModeValue("white", "gray.700");
  const boxAccentColor = useColorModeValue("gray.200", "gray.900");

  return (
    <Box
      backgroundColor={boxBgColor}
      boxShadow="base"
      dropShadow={boxAccentColor}
      borderRadius="xl"
      className="p-6 shadow-sm"
    >
      {isLoading ? <CircularProgress isIndeterminate /> : <MessageTable messages={messages} />}
    </Box>
  );
};

export { UserMessagesCell };
