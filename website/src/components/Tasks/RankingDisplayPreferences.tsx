import {
  Box,
  Flex,
  FormControl,
  FormLabel,
  NumberDecrementStepper,
  NumberIncrementStepper,
  NumberInput,
  NumberInputField,
  NumberInputStepper,
  Radio,
  RadioGroup,
  Slider,
  SliderFilledTrack,
  SliderThumb,
  SliderTrack,
  Stack,
  Switch,
  Text,
  Tooltip,
  useColorModeValue,
} from "@chakra-ui/react";
import { useTranslation } from "next-i18next";
import { useCallback } from "react";
import { useRankingDisplayPreferences } from "src/hooks/tasks/useRankingDisplayPreferences";

interface RankingDisplayPreferencesProps {
  maxMessagesPerRow?: number;
}

export const RankingDisplayPreferences = ({ maxMessagesPerRow = 6 }: RankingDisplayPreferencesProps) => {
  const { t } = useTranslation("tasks");
  const {
    preferences,
    setDisplayMode,
    setRemoveContentLimit,
    setMessagesPerRow,
  } = useRankingDisplayPreferences();

  const cardColor = useColorModeValue("gray.50", "gray.800");

  const handleDisplayModeChange = useCallback((value: string) => {
    setDisplayMode(value as "vertical" | "horizontal");
  }, [setDisplayMode]);

  const handleContentLimitToggle = useCallback((checked: boolean) => {
    setRemoveContentLimit(checked);
  }, [setRemoveContentLimit]);

  const handleMessagesPerRowChange = useCallback((value: number) => {
    setMessagesPerRow(value);
  }, [setMessagesPerRow]);

  const handleSliderChange = useCallback((value: number) => {
    setMessagesPerRow(value);
  }, [setMessagesPerRow]);

  return (
    <Box p="4" borderRadius="lg" bg={cardColor} mb="4">
      <Text fontSize="md" fontWeight="semibold" mb="4">
        {t("ranking_display_preferences")}
      </Text>
      
      <Stack spacing="4">
        {/* Display Mode Toggle */}
        <FormControl>
          <FormLabel mb="2">{t("display_mode")}</FormLabel>
          <RadioGroup value={preferences.displayMode} onChange={handleDisplayModeChange}>
            <Stack direction="row" spacing="6">
              <Radio value="vertical">{t("vertical_display")}</Radio>
              <Radio value="horizontal">{t("horizontal_display")}</Radio>
            </Stack>
          </RadioGroup>
        </FormControl>

        {/* Remove Content Limit Toggle */}
        <FormControl>
          <Flex justifyContent="space-between" alignItems="center">
            <FormLabel mb="0">{t("remove_content_limit")}</FormLabel>
            <Switch
              isChecked={preferences.removeContentLimit}
              onChange={(e) => handleContentLimitToggle(e.target.checked)}
            />
          </Flex>
        </FormControl>

        {/* Messages Per Row Slider (only show in horizontal mode) */}
        {preferences.displayMode === "horizontal" && (
          <FormControl>
            <FormLabel mb="2">
              <Tooltip label={t("messages_per_row_description")} placement="top">
                {t("messages_per_row")}
              </Tooltip>
            </FormLabel>
            <Flex gap="4" alignItems="center">
              <Slider
                aria-label={t("messages_per_row")}
                min={1}
                max={maxMessagesPerRow}
                step={1}
                value={preferences.messagesPerRow}
                onChange={handleSliderChange}
                focusThumbOnChange={false}
                flex="1"
              >
                <SliderTrack>
                  <SliderFilledTrack />
                </SliderTrack>
                <SliderThumb />
              </Slider>
              <NumberInput
                value={preferences.messagesPerRow}
                onChange={(_, value) => handleMessagesPerRowChange(value)}
                size="sm"
                maxW="80px"
                min={1}
                max={maxMessagesPerRow}
                step={1}
              >
                <NumberInputField />
                <NumberInputStepper>
                  <NumberIncrementStepper />
                  <NumberDecrementStepper />
                </NumberInputStepper>
              </NumberInput>
            </Flex>
          </FormControl>
        )}
      </Stack>
    </Box>
  );
};
