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
  useDisclosure,
} from "@chakra-ui/react";
import { Settings } from "lucide-react";
import { useTranslation } from "next-i18next";
import { ChangeEvent, memo, useCallback } from "react";
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

const parameterLabelExplanation: Record<keyof SamplingParameters, string> = {
  max_new_tokens: "Max new tokens: This parameter tells the model how many new tokens it should generate at most for the response.",
  top_k: "Top-k: This is similar to top-p sampling, but instead of taking the top tokens until their cumulative probability exceeds \"p\", it only takes the K most probable tokens. Top-p is usually preferred since it allows the model to \"tune\" the search radius, but top-k can be useful as an emergency break when the model has no idea what to generate next and assigns a very uniform distribution to many tokens.",
  top_p: "Top-p (also known as nucleus) sampling: This method reduces the probability distribution to only look at the top-p percent of tokens. By discarding low probability tokens, it helps to bound the generation and prevent the model from generating grammatically incorrect sentences.",
  temperature: "Temperature: Each token you generate is sampled from a distribution p(next_token|previous_tokens). The temperature parameter can \"sharpen\" or dampen this distribution. Setting it to 1 means that the model generates tokens based on their predicted probability (i.e., if the model predicts that \"XYZ\" has a probability of 12.3%, it will generate it with a 12.3% likelihood). Lowering the temperature towards zero makes the model more greedy, causing high probabilities to get even higher and low probabilities to get even lower (note that this is not a linear relationship!). Increasing the temperature makes all probabilities more similar. Intuitively, a low temperature means that the model generates responses that align closely with its beliefs, while a high temperature allows for more creative and diverse responses.",
  repetition_penalty: "Repetition Penalty: This parameter reduces the probability of repeating the same tokens again and again by making repeated tokens less likely than the model would ordinarily predict.",
  typical_p: "Typical p: Typical sampling is an information-theoretic technique that, in addition to the probability, also considers the sequence entropy (i.e., the information content according to the probability). This means that typical sampling \"overweights\" some of the tokens with lower probability because they are deemed \"interesting,\" and underweights high probability tokens because they are deemed \"boring.\"",
};

const ChatConfigForm = () => {
  const { t } = useTranslation("chat");
  const { modelInfos } = useChatContext();

  const { control, register, reset, getValues } = useFormContext<ChatConfigFormData>();
  const selectedModel = useWatch({ name: "model_config_name", control: control });
  const presets = modelInfos.find((model) => model.name === selectedModel)!.parameter_configs;

  const handlePresetChange = useCallback(
    (e: ChangeEvent<HTMLSelectElement>) => {
      const newPresetName = e.target.value;
      const config =
        newPresetName === customPresetName
          ? customPresetDefaultValue
          : presets.find((preset) => preset.name === newPresetName)!.sampling_parameters;
      reset({ ...config, model_config_name: selectedModel });
    },
    [presets, reset, selectedModel]
  );

  const selectedPresetName =
    presets.find((preset) => areParametersEqual(preset.sampling_parameters, getValues()))?.name ?? customPresetName;

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
};

const ChatParameterField = memo(function ChatParameterField(props: NumberInputSliderProps) {
  const { max = 1, precision = 2, step = 0.01, min = 0, value, isDisabled, name, onChange } = props;

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
  const labelExplanation = parameterLabelExplanation[name];
  const showSlider = value !== null;

  return (
    <FormControl isDisabled={isDisabled}>
      <Flex justifyContent="space-between" mb="2">
        <FormLabel mb="0" title={labelExplanation}>{label}</FormLabel>
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
