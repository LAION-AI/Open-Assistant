import { Icon, Progress, Stack, Text, Textarea, TextareaProps, Tooltip, useColorModeValue } from "@chakra-ui/react";
import lande from "lande";
import Link from "next/link";
import { useTranslation } from "next-i18next";
import React from "react";
import TextareaAutosize, { TextareaAutosizeProps } from "react-textarea-autosize";
import { useCurrentLocale } from "src/hooks/locale/useCurrentLocale";
import { LanguageAbbreviations } from "src/lib/iso6393";
import { getLocaleDisplayName } from "src/lib/languages";
import { colors } from "src/styles/Theme/colors";

interface TrackedTextboxProps {
  text: string;
  thresholds: {
    low: number;
    medium: number;
    goal: number;
  };
  textareaProps?: TextareaProps & TextareaAutosizeProps;
  onTextChange: (event: React.ChangeEvent<HTMLTextAreaElement>) => void;
}

export const TrackedTextarea = (props: TrackedTextboxProps) => {
  const { t } = useTranslation("tasks");
  const wordLimitForLangDetection = 4;
  const backgroundColor = useColorModeValue("gray.100", "gray.900");
  const currentLanguage = useCurrentLocale();
  const wordCount = (props.text.match(/\w+/g) || []).length;

  const detectLang = (text: string) => {
    try {
      return LanguageAbbreviations[lande(text)[0][0]] || currentLanguage;
    } catch (error) {
      return currentLanguage;
    }
  };
  const detectedLang = wordCount > wordLimitForLangDetection ? detectLang(props.text) : currentLanguage;
  const wrongLanguage = detectedLang !== currentLanguage;

  let progressColor: string;
  switch (true) {
    case wordCount < props.thresholds.low:
      progressColor = "red";
      break;
    case wordCount < props.thresholds.medium:
      progressColor = "yellow";
      break;
    default:
      progressColor = "green";
  }

  const problemColor = useColorModeValue(colors.light.problem, colors.dark.problem);

  return (
    <Stack direction={"column"}>
      <div style={{ position: "relative" }}>
        <Textarea
          backgroundColor={backgroundColor}
          border="none"
          data-cy="reply"
          p="4"
          value={props.text}
          onChange={props.onTextChange}
          autoFocus
          {...props.textareaProps}
          as={TextareaAutosize}
        />
        <div
          style={{
            fontSize: "0.7em",
            fontWeight: "bold",
            color: wrongLanguage ? problemColor : "gray",
            position: "absolute",
            top: 0,
            marginTop: "0.1em",
            left: 0, // Attach to left and right and align to end to support rtl languages
            right: 0,
            marginInlineEnd: "0.5em",
            textAlign: "end",
            zIndex: 1, // Appear above the text box when it has focus
            textTransform: "uppercase",
          }}
        >
          <Tooltip
            label={t(wrongLanguage ? "writing_wrong_langauge_a_b" : "submitted_as", {
              submit_lang: getLocaleDisplayName(currentLanguage),
              detected_lang: getLocaleDisplayName(detectedLang, currentLanguage),
            })}
          >
            {detectedLang}
          </Tooltip>
        </div>
      </div>

      <Link href="https://www.markdownguide.org/basic-syntax" rel="noopener noreferrer nofollow" target="_blank">
        <Stack direction={"row"} align={"center"}>
          <Icon height={"1em"} viewBox={"0 0 1em 1em"}>
            <path d="M14.85 3c.63 0 1.15.52 1.14 1.15v7.7c0 .63-.51 1.15-1.15 1.15H1.15C.52 13 0 12.48 0 11.84V4.15C0 3.52.52 3 1.15 3ZM9 11V5H7L5.5 7 4 5H2v6h2V8l1.5 1.92L7 8v3Zm2.99.5L14.5 8H13V5h-2v3H9.5Z"></path>
          </Icon>
          <Text fontSize={"0.7em"}>{t("default.markdownguide")}</Text>
        </Stack>
      </Link>
      <Progress
        size={"md"}
        height={"2"}
        width={"100%"}
        rounded={"md"}
        value={wordCount}
        colorScheme={progressColor}
        max={props.thresholds.goal}
      />
    </Stack>
  );
};
