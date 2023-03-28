import { inferenceClient } from "src/lib/oasst_inference_client";
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
  >(
    "/chat/vote",
    (
      _,
      {
        arg,
      }: {
        arg: {
          message_id: string;
          chat_id: string;
          score: number;
        };
      }
    ) => {
      inferenceClient.vote(arg);
    }
  );
  return trigger;
};
