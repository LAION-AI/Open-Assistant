import { OasstInferenceClient } from "src/lib/oasst_inference_client";
import useSWR from "swr";

import { useInferenceAuth } from "./useInferenceAuth";

export const useFetchChatList = () => {
  const { isAuthenticated } = useInferenceAuth();

  console.log("isAuthenticated", isAuthenticated);

  return useSWR(isAuthenticated ? "/chat" : null, () => new OasstInferenceClient().get_my_chats(), {
    revalidateOnFocus: true,
  });
};
