import { Tooltip } from "@chakra-ui/react";
import { Progress, Stack, Textarea, TextareaProps, useColorModeValue } from "@chakra-ui/react";
import lande from "lande";
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
      <Progress
        size={"md"}
        height={"2"}
        rounded={"md"}
        value={wordCount}
        colorScheme={progressColor}
        max={props.thresholds.goal}
      />
    </Stack>
  );
};
