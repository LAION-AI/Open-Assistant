import { OasstInferenceClient } from "src/lib/oasst_inference_client";
import useSWR from "swr";

export const useInferenceAuth = () => {
  const { data, isLoading, mutate } = useSWR<boolean>("/auth/check", () => {
    return new OasstInferenceClient().check_auth();
  });

  return {
    isAuthenticated: data,
    isLoading,
    mutate,
  };
};
