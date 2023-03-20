import { post } from "src/lib/api";
import { API_ROUTES } from "src/lib/routes";
import useSWRMutation from "swr/mutation";

export const useMessageVote = () => {
  const { trigger } = useSWRMutation<
    any,
    any,
    any,
    {
      message_id: string;
      chat_id: string;
      score: number;
    }
  >(API_ROUTES.CHAT_MESSAGE_VOTE, post);
  return trigger;
};
