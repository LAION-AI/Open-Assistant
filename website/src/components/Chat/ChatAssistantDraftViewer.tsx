import { Avatar, Box, Button, Collapse, Divider, Flex, Tag, useColorModeValue } from "@chakra-ui/react";
import { useTranslation } from "next-i18next";
import { lazy, ReactNode, useState } from "react";
import { InferenceMessage } from "src/types/Chat";

import { PluginUsageDetails } from "../Messages/PluginUsageDetails";
import { WorkParametersDisplay } from "./WorkParameters";
const RenderedMarkdown = lazy(() => import("../Messages/RenderedMarkdown"));

type OnDraftPickedFn = (message_index: number) => void;

type ChatAssistantDraftViewerProps = {
  streamedDrafts: string[];
  isComplete: boolean;
  draftMessages: InferenceMessage[];
  onDraftPicked: OnDraftPickedFn;
  pager: ReactNode;
};

export const ChatAssistantDraftViewer = ({
  streamedDrafts,
  isComplete,
  draftMessages,
  onDraftPicked,
  pager,
}: ChatAssistantDraftViewerProps) => {
  const { t } = useTranslation(["chat", "common"]);

  const [expandedMessage, setExpandedMessage] = useState<number>(0);
  const handleToggleExpand = (index) => {
    setExpandedMessage(index === expandedMessage ? -1 : index);
  };

  const containerBackgroundColor = useColorModeValue("#DFE8F1", "#42536B");
  const draftHoverBackgroundColor = useColorModeValue("gray.300", "blackAlpha.300");

  return (
    <Flex
      width={"full"}
      gap={0.5}
      flexDirection={{ base: "column", md: "row" }}
      alignItems={"start"}
      position={"relative"}
      padding={{ base: 3, md: 0 }}
      background={{ base: containerBackgroundColor, md: "transparent" }}
      borderRadius={{ base: "18px", md: 0 }}
      maxWidth={{ base: "3xl", "2xl": "4xl" }}
    >
      <Avatar
        size={{ base: "xs", md: "sm" }}
        marginRight={{ base: 0, md: 2 }}
        marginTop={{ base: 0, md: `6px` }}
        marginBottom={{ base: 1.5, md: 0 }}
        borderColor={"blackAlpha.200"}
        _dark={{ backgroundColor: "blackAlpha.300" }}
        src="/images/logos/logo.png"
      />
      <Flex
        background={containerBackgroundColor}
        borderRadius={{ base: 0, md: "18px" }}
        gap={1}
        width={"full"}
        padding={{ base: 0, md: 4 }}
        flexDirection={"column"}
        overflowX={"auto"}
      >
        {(isComplete && draftMessages.length !== 0
          ? (draftMessages.map((message) => ({ content: message.content, used_plugin: message.used_plugin })) as {
              content: string;
              used_plugin: object | null;
            }[])
          : (streamedDrafts.map((message) => ({ content: message, used_plugin: null })) as {
              content: string;
              used_plugin: object | null;
            }[])
        ).map(({ content, used_plugin }, index) => (
          <>
            <Box
              key={`draft-message-${index}`}
              borderRadius={"md"}
              padding={2}
              gap={2}
              width={"full"}
              rounded={"md"}
              cursor={"pointer"}
              onClick={() => onDraftPicked(index)}
              _hover={{ backgroundColor: draftHoverBackgroundColor }}
              transition={"background-color 0.2 ease-in-out"}
            >
              <Tag size={"md"} variant={"outline"} maxWidth={"max-content"} marginBottom={1.5} borderRadius={"full"}>
                {t("draft", { ns: "chat" })} {index + 1}
              </Tag>
              <Collapse startingHeight={100} in={expandedMessage === index}>
                <Box
                  bgGradient={
                    expandedMessage === index
                      ? "linear(to-b, #000000, #000000)"
                      : "linear(to-b, #000000 40px, #00000000 95px)"
                  }
                  _dark={{
                    bgGradient:
                      expandedMessage === index
                        ? "linear(to-b, #FFFFFF, #FFFFFF)"
                        : "linear(to-b, #FFFFFF 40px, #00000000 95px)",
                  }}
                  backgroundClip={"text"}
                  padding={0}
                  minHeight={"100px"}
                  gap={0}
                >
                  {isComplete ? (
                    <>
                      <PluginUsageDetails usedPlugin={used_plugin} />
                      <RenderedMarkdown markdown={content} disallowedElements={[]}></RenderedMarkdown>
                    </>
                  ) : (
                    content
                  )}
                </Box>
              </Collapse>
              <Button
                size={"sm"}
                width={"fit-content"}
                marginTop="1rem"
                marginLeft={"auto"}
                background={"white"}
                _dark={{
                  background: "gray.500",
                }}
                onClick={(e) => {
                  e.stopPropagation();
                  handleToggleExpand(index);
                }}
              >
                {expandedMessage === index ? t("show_less", { ns: "common" }) : t("show_more", { ns: "common" })}
              </Button>
            </Box>
            {index !== streamedDrafts.length - 1 && (
              <Divider
                key={`divider-${index}`}
                marginY="2.0"
                borderColor="blackAlpha.300"
                _dark={{
                  borderColor: "blackAlpha.700",
                }}
              />
            )}
          </>
        ))}
        {pager}
        {draftMessages && draftMessages.length !== 0 && draftMessages[0]?.work_parameters && (
          <WorkParametersDisplay parameters={draftMessages[0].work_parameters} />
        )}
      </Flex>
    </Flex>
  );
};
