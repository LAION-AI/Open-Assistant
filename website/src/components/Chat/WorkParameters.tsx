import { Accordion, AccordionButton, AccordionItem, AccordionPanel, Divider, Flex, Text } from "@chakra-ui/react";
import { ChevronDown } from "lucide-react";
import { useTranslation } from "next-i18next";
import { memo } from "react";
import { JsonCard } from "src/components/JsonCard";
import { InferenceMessage, SamplingParameters } from "src/types/Chat";

export const areParametersEqual = (a: SamplingParameters, b: SamplingParameters) => {
  return (
    a.top_k === b.top_k &&
    a.top_p === b.top_p &&
    a.typical_p === b.typical_p &&
    a.temperature === b.temperature &&
    a.repetition_penalty === b.repetition_penalty &&
    a.max_new_tokens === b.max_new_tokens
  );
};

export const WorkParametersDisplay = memo(function WorkParametersDisplay({
  parameters,
}: {
  parameters: NonNullable<InferenceMessage["work_parameters"]>;
}) {
  const { seed: _, ...rest } = parameters;
  const model_id = parameters.model_config.model_id.replace("OpenAssistant/", "");
  const { t } = useTranslation("chat");

  return (
    <>
      <Divider
        my="0.5"
        borderColor="blackAlpha.300"
        _dark={{
          borderColor: "blackAlpha.700",
        }}
      />
      <Accordion allowToggle>
        <AccordionItem border="none">
          <Flex
            justifyContent="space-between"
            alignItems="end"
            textColor="gray.600"
            _dark={{
              textColor: "gray.400",
            }}
          >
            <Flex gap="4" flexGrow="1" fontSize="sm" w="full">
              <span>
                {t("model")}:{" "}
                <Text as="span" fontWeight="medium">
                  {model_id}
                </Text>
              </span>
            </Flex>
            <AccordionButton
              as={ChevronDown}
              borderRadius="md"
              w="auto"
              p="0.5"
              size="24px"
              bg="inherit"
              flexGrow={0}
            />
          </Flex>
          <AccordionPanel p="0" pt="1">
            <JsonCard fontSize="sm" bodyProps={{ p: 3 }}>
              {rest}
            </JsonCard>
          </AccordionPanel>
        </AccordionItem>
      </Accordion>
    </>
  );
});
