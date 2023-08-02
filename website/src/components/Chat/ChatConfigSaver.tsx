import { MutableRefObject, useEffect } from "react";
import { useFormContext } from "react-hook-form";
import { ChatConfigFormData, PluginEntry, CustomInstructionsType } from "src/types/Chat";
import { CachedChatConfig, CustomPreset, setConfigCache } from "src/utils/chat";

export const ChatConfigSaver = ({
  selectedPresetName,
  hyrated,
  plugins,
  customPresets,
  customInstructions,
}: {
  selectedPresetName: string;
  hyrated: MutableRefObject<boolean>;
  plugins: PluginEntry[];
  customPresets: CustomPreset[];
  customInstructions: CustomInstructionsType;
}) => {
  const { getValues, watch } = useFormContext<ChatConfigFormData>();
  const { model_config_name, plugins: selectedPlugins, ...preset_config } = { ...watch(), ...getValues() };
  useEffect(() => {
    if (hyrated.current) {
      const config: CachedChatConfig = {
        model_config_name,
        plugins: plugins.filter((p) => !p.trusted), // only save non-trusted, custom plugins
        selectedPresetName,
        custom_presets: customPresets,
        custom_preset_config: preset_config,
        selectedPlugins: selectedPlugins,
        custom_instructions: customInstructions,
      };
      setConfigCache(config);
    }
  }, [
    customPresets,
    hyrated,
    model_config_name,
    plugins,
    preset_config,
    selectedPlugins,
    selectedPresetName,
    customInstructions,
  ]);

  return null;
};
