import { useEffect } from "react";
import { useFormContext } from "react-hook-form";
import { setConfigCache } from "src/hooks/chat/useCacheConfig";
import { ChatConfigFormData } from "src/types/Chat";

export const ChatConfigSaver = () => {
  const { watch } = useFormContext<ChatConfigFormData>();
  const config = watch();
  console.log("ChatConfigSaver", config);
  useEffect(() => {
    setConfigCache(config);
  }, [config]);

  return null;
};
