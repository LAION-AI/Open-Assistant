import {
  CircularProgress,
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
  useDisclosure,
} from "@chakra-ui/react";
import { Settings } from "lucide-react";
import { useTranslation } from "next-i18next";
import { useCallback, useState } from "react";
import { Controller, useForm, UseFormReturn } from "react-hook-form";
import { get } from "src/lib/api";
import { API_ROUTES } from "src/lib/routes";
import { ModelInfo, WorkParametersInput } from "src/types/Chat";
import useSWRImmutable from "swr/immutable";
import { StrictOmit } from "ts-essentials";

import { ChatConversation } from "./ChatConversation";

type UseChatConfigForm = UseFormReturn<WorkParametersInput>;

export const ChatSection = ({ chatId }: { chatId: string }) => {
  const { control, getValues, register, setValue } = useForm<WorkParametersInput>({
    defaultValues: {
      temperature: 0.7,
      top_p: 1,
      top_k: 0,
      repetition_penalty: 0,
      max_new_tokens: 256,
    },
  });

  return (
    <>
      <ChatConversation chatId={chatId} getConfigValues={getValues} />
      <ChatConfigDrawer control={control} register={register} setValue={setValue}></ChatConfigDrawer>
    </>
  );
};

type ChatConfigDrawerProps = Pick<UseChatConfigForm, "control" | "register" | "setValue">;

const ChatConfigDrawer = ({ control, register, setValue }: ChatConfigDrawerProps) => {
  const { isOpen, onOpen, onClose } = useDisclosure();
  const { data, isLoading } = useSWRImmutable<ModelInfo[]>(API_ROUTES.GET_CHAT_MODELS, get, {
    onSuccess(models) {
      const model = models[0];

      model && setValue("model_name", model.name);
    },
  });
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
          aria-label={t("chat_config.title")}
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
          <DrawerHeader borderBottomWidth="1px">{t("chat_config.title")}</DrawerHeader>
          <DrawerBody>
            {isLoading && !data && <CircularProgress></CircularProgress>}
            {data && <ChatConfigForm modelInfos={data} control={control} register={register}></ChatConfigForm>}
          </DrawerBody>
        </DrawerContent>
      </Drawer>
    </>
  );
};

const sliderItems = [
  {
    key: "temperature",
  },
  {
    key: "max_new_tokens",
    max: 1000,
    step: 1,
    min: 1,
  },
  {
    key: "top_p",
  },
  {
    key: "repetition_penalty",
  },
  {
    key: "top_k",
  },
] as const;

const ChatConfigForm = ({
  modelInfos,
  control,
  register,
}: { modelInfos: ModelInfo[] } & StrictOmit<ChatConfigDrawerProps, "setValue">) => {
  const { t } = useTranslation("chat");
  return (
    <Stack gap="4">
      <FormControl>
        <FormLabel>{t("chat_config.model")}</FormLabel>
        <Select {...register("model_name")}>
          {modelInfos.map(({ name }) => (
            <option value={name} key={name}>
              {name}
            </option>
          ))}
        </Select>
      </FormControl>
      {sliderItems.map((item) => (
        <Controller
          name={item.key}
          key={item.key}
          control={control}
          render={({ field }) => (
            <NumberInputSlider label={t(`chat_config.${item.key}`)} {...item} {...field}></NumberInputSlider>
          )}
        ></Controller>
      ))}
    </Stack>
  );
};

type NumberInputSliderProps = {
  label: string;
  max?: number;
  min?: number;
  precision?: number;
  step?: number;
  onChange: (value: number) => void;
  value: number | null;
};

// eslint-disable-next-line react/display-name
const NumberInputSlider = (props: NumberInputSliderProps) => {
  const { label, max = 1, precision = 2, step = 0.01, min = 0, value: propsValue } = props;
  const [value, setValue] = useState(propsValue || 0);
  const handleChange = useCallback(
    (val: string | number) => {
      const newVal = Number(val);
      setValue(newVal);
      props.onChange(newVal);
    },
    [props]
  );
  return (
    <FormControl>
      <Flex justifyContent="space-between" mb="2">
        <FormLabel mb="0">{label}</FormLabel>
        <NumberInput
          value={value}
          onChange={handleChange}
          size="xs"
          maxW={20}
          precision={precision}
          step={step}
          min={min}
          max={max}
        >
          <NumberInputField />
          <NumberInputStepper>
            <NumberIncrementStepper height="12px" />
            <NumberDecrementStepper />
          </NumberInputStepper>
        </NumberInput>
      </Flex>
      <Slider aria-label={label} min={min} max={max} step={step} value={value} onChange={handleChange}>
        <SliderTrack>
          <SliderFilledTrack />
        </SliderTrack>
        <SliderThumb />
      </Slider>
    </FormControl>
  );
};
