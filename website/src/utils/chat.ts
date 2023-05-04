import { PluginEntry } from "src/types/Chat";
import { SamplingParameters } from "src/types/Chat";

const CHAT_CONFIG_KEY = "CHAT_CONFIG";

export type CachedChatConfig = {
  model_config_name: string;
  selectedPreset: string;
  custom_preset_config: SamplingParameters;
  custom_presets: Array<{ name: string; config: SamplingParameters }>;
  selectedPlugins: PluginEntry[];
  plugins: PluginEntry[]; // all plugins user added
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

    if (parsed && "top_k" in parsed) {
      // legacy config
      localStorage.removeItem(CHAT_CONFIG_KEY);
      return null;
    }

    return parsed;
  }
  return null;
};
