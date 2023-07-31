import { PluginEntry } from "src/types/Chat";
import { SamplingParameters, CustomInstructionsType } from "src/types/Chat";

const CHAT_CONFIG_KEY = "CHAT_CONFIG_V2";

export type CustomPreset = { name: string; config: SamplingParameters };

export type CachedChatConfig = {
  model_config_name: string;
  selectedPresetName: string;
  custom_preset_config: SamplingParameters;
  custom_presets: CustomPreset[];
  selectedPlugins: PluginEntry[];
  plugins: PluginEntry[]; // all plugins user added
  custom_instructions: CustomInstructionsType;
};

export const setConfigCache = (config: CachedChatConfig) => {
  if (typeof localStorage !== "undefined") {
    localStorage.setItem(CHAT_CONFIG_KEY, JSON.stringify(config));
  }
};

export const getConfigCache = (): CachedChatConfig | null => {
  if (typeof localStorage !== "undefined") {
    const config = localStorage.getItem(CHAT_CONFIG_KEY);
    const parsed = config ? JSON.parse(config) : null;

    return parsed;
  }
  return null;
};
