import React, { useState, lazy, useRef } from "react";
import { Box, Button, Tooltip, Collapse, VStack, HStack, Code, Text, useColorModeValue } from "@chakra-ui/react";
import { ChevronDownIcon, ChevronUpIcon, AttachmentIcon, WarningIcon, CheckCircleIcon } from "@chakra-ui/icons";
import { useTranslation } from "next-i18next";

const SyntaxHighlighter = lazy(() => import("./SyntaxHighlighter"));

// TODO: Delete me!
const measureDivWidth = (div: HTMLDivElement | null) => {
  if (!div) return 0;
  const width = div?.parentElement?.offsetWidth - 15;
  return width;
};

const DropdownItem = ({ plugin }) => {
  const [isOpen, setIsOpen] = useState(false);
  const [innerMonologueCollapser, setInnerMonologueCollapser] = useState(false);
  const [finalPluginOutputCollapser, setFinalPluginOutputCollapser] = useState(true);
  const [finalPromptCollapser, setFinalPromptCollapser] = useState(false);
  const toggle = () => setIsOpen(!isOpen);
  const { t } = useTranslation("chat");
  const divRef = useRef<HTMLDivElement | null>(null);

  return (
    <Box ref={divRef}>
      <Button onClick={toggle} rightIcon={isOpen ? <ChevronUpIcon /> : <ChevronDownIcon />}>
        <HStack spacing={2}>
          <Text>
            <Box as="b" fontWeight="normal">
              {t("used")}
            </Box>
            <Box as="b" fontWeight="bold">
              {` ${plugin.name}`}
            </Box>
          </Text>
          <AttachmentIcon
            color={plugin.execution_details?.final_generation_assisted ? "green.500" : "red.500"}
            boxSize={5}
          />
          {JSON.stringify(plugin)}
          {!plugin?.trusted ? (
            <Tooltip label={t("unverified_plugin_description")}>
              <Box display="flex" alignItems="center" marginLeft="2" bg="red.200" borderRadius="md" p={1}>
                <WarningIcon boxSize="4" color="red.600" />
                <Text color="red.700" ml={2} mr={2} fontSize="xs">
                  {t("unverified_plugin")}
                </Text>
              </Box>
            </Tooltip>
          ) : (
            <Tooltip label={t("verified_plugin_description")}>
              <Box display="flex" alignItems="center" marginLeft="2" bg="green.200" borderRadius="md" p={1}>
                <CheckCircleIcon boxSize="4" color="green.500" />
                <Text color="green.700" ml={2} mr={2} fontSize="xs">
                  {t("verified_plugin")}
                </Text>
              </Box>
            </Tooltip>
          )}
        </HStack>
      </Button>
      <Collapse in={isOpen}>
        <Box bg={useColorModeValue("gray.100", "gray.700")} p={2} mt={2} borderRadius="md">
          <Box overflowX="auto" width={measureDivWidth(divRef.current)}>
            <Button
              width="100%"
              onClick={() => setInnerMonologueCollapser(!innerMonologueCollapser)}
              rightIcon={innerMonologueCollapser ? <ChevronUpIcon /> : <ChevronDownIcon />}
              mb={2}
            >
              <Text fontWeight="bold" mt={2} mb={1} color={"blue.300"}>
                {"inner_monologue"}
              </Text>
            </Button>
            <Collapse in={innerMonologueCollapser}>
              {plugin.execution_details?.inner_monologue.map((monologue, index) => (
                <Box as="pre" key={index} border="1px solid" whiteSpace="pre-wrap" overflowWrap="break-word" p={2}>
                  {monologue}
                </Box>
              ))}
            </Collapse>
            <Button
              width="100%"
              onClick={() => setFinalPluginOutputCollapser(!finalPluginOutputCollapser)}
              rightIcon={finalPluginOutputCollapser ? <ChevronUpIcon /> : <ChevronDownIcon />}
              mb={2}
            >
              <Text fontWeight="bold" mt={2} mb={1} color={"orange.300"}>
                {"final_plugin_output"}
              </Text>
            </Button>
            <Collapse in={finalPluginOutputCollapser}>
              <Box as="pre" border="1px solid" whiteSpace="pre-wrap" overflowWrap="break-word" p={2}>
                {plugin.execution_details?.final_tool_output}
              </Box>
            </Collapse>
            <Button
              width="100%"
              onClick={() => setFinalPromptCollapser(!finalPromptCollapser)}
              rightIcon={finalPromptCollapser ? <ChevronUpIcon /> : <ChevronDownIcon />}
              mb={2}
            >
              <Text fontWeight="bold" mt={2} mb={1} color={"green.300"}>
                {"final_prompt"}
              </Text>
            </Button>
            <Collapse in={finalPromptCollapser}>
              <Box as="pre" border="1px solid" whiteSpace="pre-wrap" overflowWrap="break-word" p={2}>
                {plugin.execution_details?.final_prompt}
              </Box>
            </Collapse>
            <Text fontWeight="bold" mt={2} mb={1} color={"grey.300"}>
              {"achieved_depth"}
            </Text>
            <Box as="pre" border="1px solid" whiteSpace="pre-wrap" overflowWrap="break-word" p={2}>
              {plugin.execution_details?.achieved_depth}
            </Box>
            <Text fontWeight="bold" mt={2} mb={1} color={"red.300"}>
              {"error_message"}
            </Text>
            <Box as="pre" border="1px solid" whiteSpace="pre-wrap" overflowWrap="break-word" p={2}>
              {plugin.execution_details?.error_message}
            </Box>
            <Text fontWeight="bold" mt={2} mb={1} color={"yellow.300"}>
              {"status"}
            </Text>
            <Box as="pre" border="1px solid" whiteSpace="pre-wrap" overflowWrap="break-word" p={2}>
              {plugin.execution_details?.status}
            </Box>
          </Box>
        </Box>
      </Collapse>
    </Box>
  );
};

export const PluginUsageDetails = ({ usedPlugin }) => {
  if (
    !usedPlugin ||
    (!usedPlugin?.execution_details?.final_generation_assisted && usedPlugin?.execution_details?.status == "success")
  )
    return;
  return (
    <VStack align="start" spacing={4} mb="15px">
      <DropdownItem key={usedPlugin.name} plugin={usedPlugin} />
    </VStack>
  );
};
