import { useEffect } from "react";
import { useFormContext } from "react-hook-form";
import { useCacheConfig } from "src/hooks/chat/useCacheConfig";
import { ChatConfigFormData } from "src/types/Chat";

export const ChatConfigSaver = () => {
  const { watch } = useFormContext<ChatConfigFormData>();
  const newValues = watch();
  const [oldValues, setConfig] = useCacheConfig();
  useEffect(() => {
    // have to compare otherwise it will cause maximum update depth exceeded
    if (JSON.stringify(oldValues) !== JSON.stringify(newValues)) {
      setConfig(newValues);
    }
  }, [setConfig, newValues, oldValues]);

  return null;
};
