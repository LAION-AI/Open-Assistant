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
import SimpleBar from "simplebar-react";
import {
  ChatConfigFormData,
  ModelParameterConfig,
  PluginEntry,
  SamplingParameters,
  CustomInstructionsType,
} from "src/types/Chat";
import { CustomPreset, getConfigCache } from "src/utils/chat";
import { useIsomorphicLayoutEffect } from "usehooks-ts";

import { ChatConfigSaver } from "./ChatConfigSaver";
import { useChatInitialData } from "./ChatInitialDataContext";
import { DeletePresetButton } from "./DeletePresetButton";
import { PluginsChooser } from "./PluginsChooser";
import CustomInstructions from "./CustomInstructions";
import { SavePresetButton } from "./SavePresetButton";
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

const unKnownCustomPresetName = "__custom__";
const customPresetNamePrefix = "$$";
const isCustomPresetName = (name: string) => name.startsWith(customPresetNamePrefix);
export const toCustomPresetName = (name: string) => `${customPresetNamePrefix}${name}`;

const parameterLabel: Record<keyof SamplingParameters, string> = {
  max_new_tokens: "Max new tokens",
  top_k: "Top K",
  top_p: "Top P",
  temperature: "Temperature",
  repetition_penalty: "Repetition Penalty",
  typical_p: "Typical P",
};

const findPresetName = (presets: ModelParameterConfig[], config: SamplingParameters) => {
  return (
    presets.find((preset) => areParametersEqual(preset.sampling_parameters, config))?.name ?? unKnownCustomPresetName
  );
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
  const [customInstructions, setCustomInstructions] = useState<CustomInstructionsType>({
    user_profile: "",
    user_response_instructions: "",
  });
  const [selectedPresetName, setSelectedPresetName] = useState(() => findPresetName(presets, getValues()));

  const { customPresets, handleSavePreset, setCustomPresets, handleDeletePreset } = useCustomPresets({
    selectedPresetName,
    setSelectedPresetName,
  });

  const { hyrated, plugins, setPlugins } = useHydrateChatConfig({
    setCustomPresets,
    setSelectedPresetName,
    setCustomInstructions,
  });

  const [lockPresetSelection, setLockPresetSelection] = useState(false);

  const handlePresetChange = useCallback(
    (e: ChangeEvent<HTMLSelectElement>) => {
      const newPresetName = e.target.value;
      if (newPresetName !== unKnownCustomPresetName) {
        const config = isCustomPresetName(newPresetName)
          ? customPresets.find((preset) => preset.name === newPresetName)!.config
          : presets.find((preset) => preset.name === newPresetName)!.sampling_parameters;

        resetParameters(setValue, config);
      }
      setSelectedPresetName(newPresetName);
    },
    [customPresets, presets, setValue]
  );

  const handleCustomInstructionsChange = useCallback(
    (value: CustomInstructionsType) => {
      setCustomInstructions(value);
      setValue("custom_instructions", value);
    },
    [setCustomInstructions]
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
      <SimpleBar
        style={{ maxHeight: "100%", height: "100%", minHeight: "0" }}
        classNames={{
          contentEl: "mr-4 flex flex-col overflow-y-auto items-center",
        }}
      >
        <Stack gap="4" maxW="full">
          <PluginsChooser plugins={plugins} setPlugins={setPlugins} />
          <CustomInstructions onChange={handleCustomInstructionsChange} savedCustomInstructions={customInstructions} />
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
              {customPresets.map(({ name }) => (
                <option value={name} key={name}>
                  {name.slice(customPresetNamePrefix.length)}
                </option>
              ))}
              <option value={unKnownCustomPresetName}>{t("preset_custom")}</option>
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
                  isDisabled={selectedPresetName !== unKnownCustomPresetName && !isCustomPresetName(selectedPresetName)}
                  description={t(("parameter_description." + name) as any)}
                />
              )}
            ></Controller>
          ))}
        </Stack>
        <ChatConfigSaver
          plugins={plugins}
          hyrated={hyrated}
          selectedPresetName={selectedPresetName}
          customPresets={customPresets}
          customInstructions={customInstructions}
        />
      </SimpleBar>
      {selectedPresetName === unKnownCustomPresetName && (
        <SavePresetButton customPresets={customPresets} onSave={handleSavePreset} />
      )}
      {isCustomPresetName(selectedPresetName) && <DeletePresetButton onClick={handleDeletePreset}></DeletePresetButton>}
    </>
  );
});

const useHydrateChatConfig = ({
  setSelectedPresetName,
  setCustomPresets,
  setCustomInstructions,
}: {
  setSelectedPresetName: (preset: string) => void;
  setCustomPresets: (presets: CustomPreset[]) => void;
  setCustomInstructions: (instructions: CustomInstructionsType) => void;
}) => {
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

    const {
      selectedPresetName,
      model_config_name,
      custom_preset_config,
      selectedPlugins,
      plugins,
      custom_presets,
      custom_instructions,
    } = cache;
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

    if (custom_presets) {
      setCustomPresets(custom_presets);
    }

    if (custom_instructions) {
      setCustomInstructions(custom_instructions);
      setValue("custom_instructions", custom_instructions);
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
      if (selectedPresetName === unKnownCustomPresetName) {
        resetParameters(setValue, custom_preset_config);
        setSelectedPresetName(selectedPresetName);
      } else if (isCustomPresetName(selectedPresetName)) {
        // we need to use `custom_presets` here instead of `customPresets`
        // since customPresets only available on the next render
        const customPreset = custom_presets?.find((preset) => preset.name === selectedPresetName)?.config;
        if (customPreset) {
          resetParameters(setValue, customPreset);
          setSelectedPresetName(selectedPresetName);
        }
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

const useCustomPresets = ({
  selectedPresetName,
  setSelectedPresetName,
}: {
  selectedPresetName: string;
  setSelectedPresetName: (preset: string) => void;
}) => {
  const { getValues, setValue } = useFormContext<ChatConfigFormData>();
  const [customPresets, setCustomPresets] = useState<CustomPreset[]>([]);

  const handleSavePreset = useCallback(
    (name: string) => {
      const prefixedName = toCustomPresetName(name);
      setCustomPresets((prev) => [...prev, { name: prefixedName, config: getValues() }]);
      setSelectedPresetName(prefixedName);
    },
    [getValues, setSelectedPresetName]
  );

  const config = getValues();

  // sync with local state
  useEffect(() => {
    const { model_config_name: _, plugins: __, ...preset_config } = config;
    if (isCustomPresetName(selectedPresetName)) {
      setCustomPresets((prev) =>
        prev.map((preset) =>
          preset.name === selectedPresetName ? { name: selectedPresetName, config: preset_config } : preset
        )
      );
    }
  }, [config, customPresets, selectedPresetName, setCustomPresets, setValue]);

  const handleDeletePreset = useCallback(() => {
    setCustomPresets((prev) => prev.filter((preset) => preset.name !== selectedPresetName));
    setSelectedPresetName(unKnownCustomPresetName);
  }, [selectedPresetName, setSelectedPresetName]);

  return {
    customPresets,
    setCustomPresets,
    handleSavePreset,
    handleDeletePreset,
  };
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
