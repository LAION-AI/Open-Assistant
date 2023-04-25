import { useEffect } from "react";
import { useFormContext } from "react-hook-form";
import { ChatConfigFormData } from "src/types/Chat";
import { setConfigCache } from "src/utils/chat";

export const ChatConfigSaver = () => {
  const { watch, formState } = useFormContext<ChatConfigFormData>();
  const config = watch();
  useEffect(() => {
    if (formState.isDirty) {
      setConfigCache(config);
    }
  }, [config, formState.isDirty]);

  return null;
};
