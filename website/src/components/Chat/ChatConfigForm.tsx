import {
  Flex,
  FormControl,
  FormLabel,
  NumberDecrementStepper,
  NumberIncrementStepper,
  NumberInput,
  NumberInputField,
  NumberInputStepper,
  Select,
  Slider,
  SliderFilledTrack,
  SliderThumb,
  SliderTrack,
  Stack,
  Switch,
  Tooltip,
} from "@chakra-ui/react";
import { useTranslation } from "next-i18next";
import { ChangeEvent, memo, useCallback, useEffect, useState } from "react";
import { Controller, useFormContext } from "react-hook-form";
import { ChatConfigFormData, ModelParameterConfig, PluginEntry, SamplingParameters } from "src/types/Chat";
import { getConfigCache } from "src/utils/chat";
import { useIsomorphicLayoutEffect } from "usehooks-ts";

import { ChatConfigSaver } from "./ChatConfigSaver";
import { useChatContext } from "./ChatContext";
import { PluginsChooser, PluginsChooserProps } from "./PluginsChooser";
import { areParametersEqual } from "./WorkParameters";
const sliderItems: Readonly<
  Array<{
    key: keyof SamplingParameters;
    max?: number;
    min?: number;
    precision?: number;
    step?: number;
  }>
> = [
  {
    key: "temperature",
    min: 0.01,
    max: 2,
  },
  {
    key: "max_new_tokens",
    max: 1024,
    step: 1,
    min: 1,
  },
  {
    key: "top_p",
  },
  {
    key: "repetition_penalty",
    min: 1,
    max: 3,
  },
  {
    key: "top_k",
    min: 5,
    max: 2000,
    step: 5,
  },
  {
    key: "typical_p",
  },
];

const customPresetName = "__custom__";
const customPresetDefaultValue: SamplingParameters = {
  max_new_tokens: 256,
  repetition_penalty: 1.2,
  temperature: 1,
  top_k: 50,
  top_p: 0.95,
  typical_p: 0.5,
};

const parameterLabel: Record<keyof SamplingParameters, string> = {
  max_new_tokens: "Max new tokens",
  top_k: "Top K",
  top_p: "Top P",
  temperature: "Temperature",
  repetition_penalty: "Repetition Penalty",
  typical_p: "Typical P",
};

const findPresetName = (presets: ModelParameterConfig[], config: SamplingParameters) => {
  return presets.find((preset) => areParametersEqual(preset.sampling_parameters, config))?.name ?? customPresetName;
};

export const ChatConfigForm = memo(function ChatConfigForm() {
  const { t } = useTranslation("chat");
  const { modelInfos } = useChatContext();

  const { control, getValues, register, setValue } = useFormContext<ChatConfigFormData>();
  const selectedModel = getValues("model_config_name"); // have to use getValues to here to access latest value
  const plugins = getValues("plugins") || [];
  const presets = modelInfos.find((model) => model.name === selectedModel)!.parameter_configs;
  const [selectedPresetName, setSelectedPresetName] = useState(() => findPresetName(presets, getValues()));
  const { hyrated, setSavedPlugins, savedPlugins } = useHydrateChatConfig({ setSelectedPresetName });

  const [lockPresetSelection, setLockPresetSelection] = useState(false);

  const handlePresetChange = useCallback(
    (e: ChangeEvent<HTMLSelectElement>) => {
      const newPresetName = e.target.value;
      if (newPresetName !== customPresetName) {
        const config = presets.find((preset) => preset.name === newPresetName)!.sampling_parameters;

        for (const [key, value] of Object.entries(config) as Array<[keyof SamplingParameters, number]>) {
          setValue(key, value);
        }
      }
      setSelectedPresetName(newPresetName);
    },
    [presets, setValue]
  );

  // Lock preset selection if any plugin is enabled
  useEffect(() => {
    const activated = plugins.some((plugin) => plugin.enabled);
    if (activated) {
      handlePresetChange({ target: { value: "k50-Plugins" } } as any);
      setSelectedPresetName(findPresetName(presets, getValues() as SamplingParameters));
      setLockPresetSelection(true);
    } else {
      setLockPresetSelection(false);
    }
  }, [presets, plugins, handlePresetChange, getValues]);

  const config = getValues(); // have to use getValues to here to access latest value
  console.log("config", config);
  // useEffect(() => {
  //   setSelectedPresetName(findPresetName(presets, config as SamplingParameters));
  // }, [config, presets]);

  const handleOnAddPlugin: PluginsChooserProps["onAddPlugin"] = useCallback(
    (newPlugin) => {
      console.log("newPlugin", newPlugin);
      setSavedPlugins((plugins) => [...plugins, newPlugin]);
    },
    [setSavedPlugins]
  );

  return (
    <>
      <Stack gap="4">
        <PluginsChooser plugins={[...plugins, ...savedPlugins]} onAddPlugin={handleOnAddPlugin} />
        <FormControl>
          <FormLabel>{t("model")}</FormLabel>
          <Select {...register("model_config_name")}>
            {modelInfos.map(({ name }) => (
              <option value={name} key={name}>
                {name}
              </option>
            ))}
          </Select>
        </FormControl>
        <FormControl>
          <FormLabel>{t("preset")}</FormLabel>
          <Select value={selectedPresetName} onChange={handlePresetChange} isDisabled={lockPresetSelection}>
            {presets.map(({ name }) => (
              <option value={name} key={name}>
                {name}
              </option>
            ))}
            <option value={customPresetName}>{t("preset_custom")}</option>
          </Select>
        </FormControl>
        {sliderItems.map((item) => (
          <Controller
            name={item.key}
            key={item.key}
            control={control}
            render={({ field: { value, onChange, name } }) => (
              <ChatParameterField
                {...item}
                value={value}
                onChange={onChange}
                name={name}
                isDisabled={selectedPresetName !== customPresetName}
                description={t(("parameter_description." + name) as any)}
              />
            )}
          ></Controller>
        ))}
      </Stack>
      <ChatConfigSaver hyrated={hyrated} isCustomPreset selectedPresetName={selectedPresetName} />
    </>
  );
});

const useHydrateChatConfig = ({ setSelectedPresetName }: { setSelectedPresetName: (preset: string) => void }) => {
  const { modelInfos } = useChatContext();
  const [hyrated, setHyrated] = useState(false);
  const { setValue } = useFormContext<ChatConfigFormData>();
  const [savedPlugins, setSavedPlugins] = useState<PluginEntry[]>([]);

  useIsomorphicLayoutEffect(() => {
    if (hyrated) return;

    setHyrated(true);
    const cache = getConfigCache();
    console.log("cache", cache);

    if (!cache) {
      return;
    }

    const { selectedPreset, model_config_name, custom_preset_config, selectedPlugins } = cache;
    const model = modelInfos.find((model) => model.name === model_config_name);

    if (model) {
      setValue("model_config_name", model_config_name);
    }
    const resetParameters = (params: SamplingParameters) => {
      for (const [key, value] of Object.entries(params) as Array<[keyof SamplingParameters, number]>) {
        setValue(key, value); // call setValue instead of setValues to avoid reset unwanted fields
      }
    };

    if (selectedPlugins && selectedPlugins.length > 0) {
      console.log(`settings selected plugins`);
      setValue("plugins", selectedPlugins);
      const preset = (model || modelInfos[0]).parameter_configs.find(
        (preset) => preset.name === "k50-Plugins"
      )?.sampling_parameters;
      if (preset) {
        resetParameters(preset);
      }
    } else {
      // only hydrate sampling params if there is no saved plugins
      if (selectedPreset === customPresetName) {
        console.log(`resetting custom preset`, custom_preset_config);
        resetParameters(custom_preset_config);
        setSelectedPresetName(customPresetName);
      } else {
        // built-in preset
        const preset = (model || modelInfos[0]).parameter_configs.find((preset) => preset.name === selectedPreset);
        if (preset) {
          console.log(`resetting built-in preset`, custom_preset_config);
          resetParameters(preset.sampling_parameters);
        }
      }
    }
  }, [modelInfos]);

  return { hyrated, savedPlugins, setSavedPlugins };
};

type NumberInputSliderProps = {
  max?: number;
  min?: number;
  precision?: number;
  step?: number;
  onChange: (value: number | null) => void;
  value: number | null;
  isDisabled: boolean;
  name: keyof SamplingParameters;
  description?: string;
};

const ChatParameterField = memo(function ChatParameterField(props: NumberInputSliderProps) {
  const { max = 1, precision = 2, step = 0.01, min = 0, value, isDisabled, description, name, onChange } = props;

  const handleChange = useCallback(
    (val: string | number) => {
      onChange(Number(val));
    },
    [onChange]
  );

  const handleShowSliderChange = useCallback(
    (e: ChangeEvent<HTMLInputElement>) => {
      const checked = e.target.checked;
      onChange(checked ? customPresetDefaultValue[name] : null);
    },
    [onChange, name]
  );
  const label = parameterLabel[name];
  const showSlider = value !== null;

  return (
    <FormControl isDisabled={isDisabled}>
      <Flex justifyContent="space-between" mb="2">
        <FormLabel mb="0">
          <Tooltip label={description} placement="left">
            {label}
          </Tooltip>
        </FormLabel>
        <Switch isChecked={showSlider} onChange={handleShowSliderChange}></Switch>
      </Flex>
      {showSlider && (
        <Flex gap="4">
          <Slider
            aria-label={label}
            min={min}
            max={max}
            step={step}
            value={value}
            onChange={handleChange}
            focusThumbOnChange={false}
            isDisabled={isDisabled}
          >
            <SliderTrack>
              <SliderFilledTrack />
            </SliderTrack>
            <SliderThumb />
          </Slider>
          <NumberInput
            value={value}
            onChange={handleChange}
            size="xs"
            maxW="80px"
            precision={precision}
            step={step}
            min={min}
            max={max}
            isDisabled={isDisabled}
          >
            <NumberInputField />
            <NumberInputStepper>
              <NumberIncrementStepper height="12px" />
              <NumberDecrementStepper />
            </NumberInputStepper>
          </NumberInput>
        </Flex>
      )}
    </FormControl>
  );
});
