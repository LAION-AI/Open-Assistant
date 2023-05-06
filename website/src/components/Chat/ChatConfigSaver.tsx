import { useEffect } from "react";
import { useFormContext } from "react-hook-form";
import { ChatConfigFormData, PluginEntry } from "src/types/Chat";
import { CachedChatConfig, setConfigCache } from "src/utils/chat";

export const ChatConfigSaver = ({
  selectedPresetName,
  hyrated,
  plugins,
}: {
  selectedPresetName: string;
  hyrated: boolean;
  plugins: PluginEntry[];
}) => {
  const { getValues, watch } = useFormContext<ChatConfigFormData>();
  const { model_config_name, plugins: selectedPlugins, ...preset_config } = { ...watch(), ...getValues() };
  console.log(`model_config_name: ${model_config_name}`);
  useEffect(() => {
    console.log("hyrated", hyrated);
    if (hyrated) {
      const config: CachedChatConfig = {
        model_config_name,
        plugins: plugins.filter((p) => !p.trusted), // only save non-trusted, custom plugins
        selectedPreset: selectedPresetName,
        custom_presets: [],
        custom_preset_config: preset_config,
        selectedPlugins: selectedPlugins,
      };
      setConfigCache(config);
      console.log("saved config", config);
    }
  }, [hyrated, model_config_name, plugins, preset_config, selectedPlugins, selectedPresetName]);

  return null;
};
