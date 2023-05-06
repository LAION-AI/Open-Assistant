import { useEffect } from "react";
import { useFormContext } from "react-hook-form";
import { ChatConfigFormData } from "src/types/Chat";
import { setConfigCache } from "src/utils/chat";

export const ChatConfigSaver = () => {
  const { watch, formState, reset } = useFormContext<ChatConfigFormData>();
  const config = watch();
  useEffect(() => {
    if (formState.isDirty) {
      setConfigCache(config);
      // unset isDirty
      reset(config);
    }
  }, [config, formState.isDirty, reset]);

  return null;
};
