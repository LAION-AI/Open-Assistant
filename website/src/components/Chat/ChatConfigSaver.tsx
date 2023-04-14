import { useEffect } from "react";
import { useFormContext } from "react-hook-form";
import { ChatConfigFormData } from "src/types/Chat";
import { setConfigCache } from "src/utils/chat";

export const ChatConfigSaver = () => {
  const { watch } = useFormContext<ChatConfigFormData>();
  const config = watch();
  useEffect(() => {
    setConfigCache(config);
  }, [config]);

  return null;
};
