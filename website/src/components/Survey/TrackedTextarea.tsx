import { Progress, Stack, TextareaProps, Tooltip, useColorModeValue } from "@chakra-ui/react";
import lande from "lande";
import { useTranslation } from "next-i18next";
import React from "react";
import { TextareaAutosizeProps } from "react-textarea-autosize";
import { useCurrentLocale } from "src/hooks/locale/useCurrentLocale";
import { LanguageAbbreviations } from "src/lib/iso6393";
import { getLocaleDisplayName } from "src/lib/languages";
import { colors } from "src/styles/Theme/colors";

import { MarkDownEditor } from "../MarkdownEditor";

interface TrackedTextboxProps {
  text: string;
  thresholds: {
    low: number;
    medium: number;
    goal: number;
  };
  textareaProps?: TextareaProps & TextareaAutosizeProps;
  onTextChange: (value: string) => void;
}

export const TrackedTextarea = (props: TrackedTextboxProps) => {
  const { t } = useTranslation("tasks");
  const wordLimitForLangDetection = 4;
  const currentLanguage = useCurrentLocale();
  const wordCount = (props.text.match(/\S+/g) || []).length;

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
        <MarkDownEditor
          value={props.text}
          onChange={props.onTextChange}
          placeholder={props.textareaProps?.placeholder}
        />
        <div
          style={{
            fontSize: "0.7em",
            fontWeight: "bold",
            color: wrongLanguage ? problemColor : "gray",
            position: "absolute",
            bottom: 4,
            marginTop: "0.1em",
            left: 10,
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
        width={"100%"}
        rounded={"md"}
        value={wordCount}
        colorScheme={progressColor}
        max={props.thresholds.goal}
      />
    </Stack>
  );
};
