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
import { ChangeEvent, memo, useCallback, useEffect, useRef, useState } from "react";
import { Controller, useFormContext, UseFormSetValue } from "react-hook-form";
import { ChatConfigFormData, ModelParameterConfig, PluginEntry, SamplingParameters } from "src/types/Chat";
import { getConfigCache } from "src/utils/chat";
import { useIsomorphicLayoutEffect } from "usehooks-ts";

import { ChatConfigSaver } from "./ChatConfigSaver";
import { useChatInitialData } from "./ChatInitialDataContext";
import { PluginsChooser } from "./PluginsChooser";
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

const resetParameters = (setValue: UseFormSetValue<ChatConfigFormData>, params: SamplingParameters) => {
  for (const [key, value] of Object.entries(params) as Array<[keyof SamplingParameters, number]>) {
    setValue(key, value); // call setValue instead of setValues to avoid reset unwanted fields
  }
};

export const ChatConfigForm = memo(function ChatConfigForm() {
  const { t } = useTranslation("chat");
  const { modelInfos } = useChatInitialData();

  const { control, getValues, register, setValue } = useFormContext<ChatConfigFormData>();
  const selectedModel = getValues("model_config_name"); // have to use getValues to here to access latest value
  const selectedPlugins = getValues("plugins");
  const presets = modelInfos.find((model) => model.name === selectedModel)!.parameter_configs;
  const [selectedPresetName, setSelectedPresetName] = useState(() => findPresetName(presets, getValues()));
  const { hyrated, plugins, setPlugins } = useHydrateChatConfig({ setSelectedPresetName });

  const [lockPresetSelection, setLockPresetSelection] = useState(false);

  const handlePresetChange = useCallback(
    (e: ChangeEvent<HTMLSelectElement>) => {
      const newPresetName = e.target.value;
      if (newPresetName !== customPresetName) {
        const config = presets.find((preset) => preset.name === newPresetName)!.sampling_parameters;
        resetParameters(setValue, config);
      }
      setSelectedPresetName(newPresetName);
    },
    [presets, setValue]
  );

  // Lock preset selection if any plugin is enabled
  useEffect(() => {
    const activated = selectedPlugins.some((plugin) => plugin.enabled);
    if (activated) {
      handlePresetChange({ target: { value: "k50-Plugins" } } as any);
      setLockPresetSelection(true);
    } else {
      setLockPresetSelection(false);
    }
  }, [presets, selectedPlugins, handlePresetChange, getValues]);

  return (
    <>
      <Stack gap="4" maxW="full">
        <PluginsChooser plugins={plugins} setPlugins={setPlugins} />
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
            render={({ field: { onChange, name } }) => (
              <ChatParameterField
                {...item}
                value={getValues(name)} // need to call getValues here, react-hook-form not trigger rerender when call setValue manually
                onChange={onChange}
                name={name}
                isDisabled={selectedPresetName !== customPresetName}
                description={t(("parameter_description." + name) as any)}
              />
            )}
          ></Controller>
        ))}
      </Stack>
      <ChatConfigSaver plugins={plugins} hyrated={hyrated} selectedPresetName={selectedPresetName} />
    </>
  );
});

const useHydrateChatConfig = ({ setSelectedPresetName }: { setSelectedPresetName: (preset: string) => void }) => {
  const { modelInfos, builtInPlugins } = useChatInitialData();
  const hyrated = useRef(false);
  const { setValue } = useFormContext<ChatConfigFormData>();
  const [plugins, setPlugins] = useState<PluginEntry[]>(builtInPlugins);

  useIsomorphicLayoutEffect(() => {
    if (hyrated.current) return;

    hyrated.current = true;
    const cache = getConfigCache();

    if (!cache) {
      return;
    }

    const { selectedPresetName, model_config_name, custom_preset_config, selectedPlugins, plugins } = cache;
    const model = modelInfos.find((model) => model.name === model_config_name);

    if (model) {
      setValue("model_config_name", model_config_name);
    }

    if (plugins) {
      // filter out duplicated with built-in plugins and dedup by url
      const dedupedCustomPlugins = [
        ...new Map(
          plugins
            .filter((plugin) => builtInPlugins.findIndex((p) => p.url === plugin.url) === -1)
            .map((item) => [item.url, item])
        ).values(),
      ];
      setPlugins([...builtInPlugins, ...dedupedCustomPlugins]);
    }

    if (selectedPlugins && selectedPlugins.length > 0) {
      setValue("plugins", selectedPlugins);
      const preset = (model || modelInfos[0]).parameter_configs.find(
        (preset) => preset.name === "k50-Plugins"
      )?.sampling_parameters;
      if (preset) {
        resetParameters(setValue, preset);
      }
    } else {
      // only hydrate sampling params if there is no selected plugins
      if (selectedPresetName === customPresetName) {
        resetParameters(setValue, custom_preset_config);
        setSelectedPresetName(selectedPresetName);
      } else {
        // built-in preset
        const preset = (model || modelInfos[0]).parameter_configs.find(
          (preset) => preset.name === selectedPresetName
        )?.sampling_parameters;
        if (preset) {
          resetParameters(setValue, preset);
          setSelectedPresetName(selectedPresetName);
        }
      }
    }
  }, [modelInfos]);

  return { hyrated, plugins, setPlugins };
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
      onChange(checked ? max : null);
    },
    [onChange, max]
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
