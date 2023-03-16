import { Button, CircularProgress, Flex, Spacer } from "@chakra-ui/react";
import { useTranslation } from "next-i18next";
import { get } from "src/lib/api";
import { FetchMessagesCursorResponse } from "src/types/Conversation";
import useSWRImmutable from "swr/immutable";

import { useCursorPagination } from "./DataTable/useCursorPagination";
import { MessageConversation } from "./Messages/MessageConversation";

const UserMessageConversation = () => {
  const { pagination, toNextPage, toPreviousPage } = useCursorPagination();
  const { t } = useTranslation("leaderboard");

  const { data, error, isLoading } = useSWRImmutable<FetchMessagesCursorResponse>(
    `/api/messages/user?cursor=${encodeURIComponent(pagination.cursor)}&direction=${pagination.direction}`, // If we want to show own deleted messages, add:  &include_deleted=true
    get,
    {
      revalidateOnMount: true,
    }
  );

  if (isLoading && !data) {
    return <CircularProgress isIndeterminate />;
  }

  if (error) {
    return <>Unable to load messages.</>;
  }

  const userMessages = data?.items || [];

  return (
    <div>
      <Flex mb="2">
        <Button onClick={() => toPreviousPage(data)} isDisabled={!data?.prev}>
          {t("previous")}
        </Button>
        <Spacer />
        <Button onClick={() => toNextPage(data)} isDisabled={!data?.next}>
          {t("next")}
        </Button>
      </Flex>
      <MessageConversation enableLink messages={userMessages} showCreatedDate />
    </div>
  );
};
export default UserMessageConversation;
