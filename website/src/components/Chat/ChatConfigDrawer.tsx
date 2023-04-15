import {
  Drawer,
  DrawerBody,
  DrawerCloseButton,
  DrawerContent,
  DrawerHeader,
  DrawerOverlay,
  Flex,
  FormControl,
  FormLabel,
  IconButton,
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
  useDisclosure,
} from "@chakra-ui/react";
import { Settings } from "lucide-react";
import { useTranslation } from "next-i18next";
import { ChangeEvent, memo, useCallback, useState } from "react";
import { Controller, useFormContext, useWatch } from "react-hook-form";
import { ChatConfigFormData, SamplingParameters } from "src/types/Chat";

import { useChatContext } from "./ChatContext";
import { areParametersEqual } from "./WorkParameters";

export const ChatConfigDrawer = memo(function ChatConfigDrawer() {
  const { isOpen, onOpen, onClose } = useDisclosure();

  const { t } = useTranslation("chat");
  return (
    <>
      <IconButton aria-label={t("config_title")} icon={<Settings />} onClick={onOpen} size="lg" borderRadius="xl" />
      <Drawer placement="right" onClose={onClose} isOpen={isOpen}>
        <DrawerOverlay />
        <DrawerContent>
          <DrawerCloseButton />
          <DrawerHeader borderBottomWidth="1px">{t("config_title")}</DrawerHeader>
          <DrawerBody>
            <ChatConfigForm />
          </DrawerBody>
        </DrawerContent>
      </Drawer>
    </>
  );
});

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
    min: 0,
    max: 1.5,
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

const ChatConfigForm = () => {
  const { t } = useTranslation("chat");
  const { modelInfos } = useChatContext();

  const { control, register, reset, getValues } = useFormContext<ChatConfigFormData>();
  const selectedModel = useWatch({ name: "model_config_name", control: control });
  const presets = modelInfos.find((model) => model.name === selectedModel)!.parameter_configs;
  const [selectedPresetName, setSelectedPresetName] = useState(
    () =>
      presets.find((preset) => areParametersEqual(preset.sampling_parameters, getValues()))?.name ?? customPresetName
  );
  const handlePresetChange = useCallback(
    (e: ChangeEvent<HTMLSelectElement>) => {
      const newPresetName = e.target.value;
      const config =
        newPresetName === customPresetName
          ? customPresetDefaultValue
          : presets.find((preset) => preset.name === newPresetName)!.sampling_parameters;
      reset({ ...config, model_config_name: selectedModel });
      setSelectedPresetName(newPresetName);
    },
    [presets, reset, selectedModel]
  );

  return (
    <Stack gap="4">
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
        <Select value={selectedPresetName} onChange={handlePresetChange}>
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
  );
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
          <Tooltip label={description}>{label}</Tooltip>
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
