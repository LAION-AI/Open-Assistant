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
  Portal,
  Select,
  Slider,
  SliderFilledTrack,
  SliderThumb,
  SliderTrack,
  Stack,
  Switch,
  useDisclosure,
} from "@chakra-ui/react";
import { Settings } from "lucide-react";
import { useTranslation } from "next-i18next";
import { ChangeEvent, useCallback, useState } from "react";
import { Controller, FormProvider, useForm, useFormContext, useWatch } from "react-hook-form";
import { WorkParametersInput } from "src/types/Chat";
import { StrictOmit } from "ts-essentials";

import { useChatContext } from "./ChatContext";
import { ChatConversation } from "./ChatConversation";

export const ChatSection = ({ chatId }: { chatId: string }) => {
  const { modelInfos } = useChatContext();
  const form = useForm<WorkParametersInput>({
    defaultValues: modelInfos[0].parameter_configs[0].work_parameters,
  });

  return (
    <FormProvider {...form}>
      <ChatConversation chatId={chatId} />
      <ChatConfigDrawer></ChatConfigDrawer>
    </FormProvider>
  );
};

const ChatConfigDrawer = () => {
  const { isOpen, onOpen, onClose } = useDisclosure();

  const { t } = useTranslation("chat");
  return (
    <>
      <Portal>
        <IconButton
          position="absolute"
          style={{
            insetInlineEnd: `52px`,
          }}
          bottom={10}
          aria-label={t("config_title")}
          icon={<Settings></Settings>}
          size="lg"
          borderRadius="2xl"
          colorScheme="blue"
          onClick={onOpen}
        ></IconButton>
      </Portal>
      <Drawer placement="right" onClose={onClose} isOpen={isOpen}>
        <DrawerOverlay />
        <DrawerContent>
          <DrawerCloseButton />
          <DrawerHeader borderBottomWidth="1px">{t("config_title")}</DrawerHeader>
          <DrawerBody>
            <ChatConfigForm></ChatConfigForm>
          </DrawerBody>
        </DrawerContent>
      </Drawer>
    </>
  );
};

const sliderItems: Readonly<
  Array<{
    key: Exclude<keyof WorkParametersInput, "model_name">;
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
  },
];

const customPresetName = "__custom__";
const customPresetDefaultValue: StrictOmit<WorkParametersInput, "model_name"> = {
  max_new_tokens: 256,
  repetition_penalty: 1.2,
  temperature: 1,
  top_k: 50 / 32000,
  top_p: 0.95,
};

const parameterLabel: Record<keyof typeof customPresetDefaultValue, string> = {
  max_new_tokens: "Max new tokens",
  top_k: "Top K",
  top_p: "Top P",
  temperature: "Temperature",
  repetition_penalty: "Repetition Penalty",
};

const ChatConfigForm = () => {
  const { t } = useTranslation("chat");
  const { modelInfos } = useChatContext();

  const { control, register, reset } = useFormContext<WorkParametersInput>();
  const selectedModel = useWatch({ name: "model_name", control: control });

  const presets = modelInfos.find((model) => model.name === selectedModel)!.parameter_configs;

  const [presetName, setPresetName] = useState<string>(presets[0].name);

  const handlePresetChange = useCallback(
    (e: ChangeEvent<HTMLSelectElement>) => {
      const newPresetName = e.target.value;
      setPresetName(newPresetName);
      if (newPresetName !== customPresetName) {
        const config = presets.find((preset) => preset.name === newPresetName)!.work_parameters;
        reset(config);
      }
    },
    [presets, reset]
  );
  return (
    <Stack gap="4">
      <FormControl>
        <FormLabel>{t("model")}</FormLabel>
        <Select {...register("model_name")}>
          {modelInfos.map(({ name }) => (
            <option value={name} key={name}>
              {name}
            </option>
          ))}
        </Select>
      </FormControl>
      <FormControl>
        <FormLabel>{t("preset")}</FormLabel>
        <Select value={presetName} onChange={handlePresetChange}>
          {[...presets].map(({ name }) => (
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
              isCustomPreset={presetName === customPresetName}
            ></ChatParameterField>
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
  onChange: (value: number) => void;
  value: number | null;
  isCustomPreset: boolean;
  name: keyof typeof customPresetDefaultValue;
};

const ChatParameterField = (props: NumberInputSliderProps) => {
  const { max = 1, precision = 2, step = 0.01, min = 0, value, isCustomPreset, name, onChange } = props;
  const { setValue: setFormValue } = useFormContext<WorkParametersInput>();
  const [showSlider, setShowSlider] = useState(false);

  const handleChange = useCallback(
    (val: string | number) => {
      const newVal = Number(val);
      // setFormValue(name, newVal);
      onChange(newVal);
    },
    [onChange]
  );

  const handleShowSliderChange = useCallback(
    (e: ChangeEvent<HTMLInputElement>) => {
      const checked = e.target.checked;
      setFormValue(name, checked ? customPresetDefaultValue[name] : null);
      setShowSlider(e.target.checked);
      if (checked && value === null) {
        // setValue(customPresetDefaultValue[name]!);
      }
    },
    [setFormValue, name, value]
  );
  const label = parameterLabel[name];

  return (
    <FormControl isDisabled={!isCustomPreset}>
      <Flex justifyContent="space-between" mb="2">
        <FormLabel mb="0">{label}</FormLabel>
        {isCustomPreset && <Switch checked={showSlider} onChange={handleShowSliderChange}></Switch>}
      </Flex>
      {(!isCustomPreset || (showSlider && value !== null)) && (
        <Flex gap="4">
          <Slider
            aria-label={label}
            min={min}
            max={max}
            step={step}
            value={value || min}
            onChange={handleChange}
            focusThumbOnChange={false}
            isDisabled={!isCustomPreset}
          >
            <SliderTrack>
              <SliderFilledTrack />
            </SliderTrack>
            <SliderThumb />
          </Slider>
          <NumberInput
            value={value || min}
            onChange={handleChange}
            size="xs"
            maxW="80px"
            precision={precision}
            step={step}
            min={min}
            max={max}
            isDisabled={!isCustomPreset}
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
};
