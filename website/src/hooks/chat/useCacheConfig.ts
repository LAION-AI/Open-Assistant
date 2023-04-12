import { useChatContext } from "src/components/Chat/ChatContext";
import { useLocalStorage } from "usehooks-ts";

const CHAT_CONFIG_KEY = "CHAT_CONFIG";

export const useCacheConfig = () => {
  const { modelInfos } = useChatContext();
  //NOTE: we should at some point validate the cache, in case models were added or deleted
  // or certain parameters disabled
  return useLocalStorage(CHAT_CONFIG_KEY, {
    ...modelInfos[0].parameter_configs[0].sampling_parameters,
    model_config_name: modelInfos[0].name,
  });
};
