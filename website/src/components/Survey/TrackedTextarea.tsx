import {} from "@chakra-ui/react";
import lande from "lande";
import { LanguageAbbreviations } from "src/lib/iso6393";
import { useCookies } from "react-cookie";
import React from "react";
import {
  Progress,
  Stack,
  Textarea,
  TextareaProps,
  useColorModeValue,
  Button,
  Modal,
  ModalBody,
  ModalCloseButton,
  ModalContent,
  ModalHeader,
  ModalOverlay,
  useDisclosure,
} from "@chakra-ui/react";

interface TrackedTextboxProps {
  text: string;
  thresholds: {
    low: number;
    medium: number;
    goal: number;
  };
  textareaProps?: TextareaProps;
  onTextChange: (event: React.ChangeEvent<HTMLTextAreaElement>) => void;
}

const killEvent = (e) => e.stopPropagation();

export const TrackedTextarea = (props: TrackedTextboxProps) => {
  const [wordLimitForLangDetection, setWordLimitForLangDetection] = React.useState(10);
  const backgroundColor = useColorModeValue("gray.100", "gray.900");
  const [cookies] = useCookies(["NEXT_LOCALE"]);
  const wordCount = (props.text.match(/\w+/g) || []).length;
  const { isOpen, onOpen, onClose } = useDisclosure();
  const currentLanguage = cookies["NEXT_LOCALE"];

  const closeTemporaryIgnoreLanguageDetection = () => {
    setWordLimitForLangDetection(2 * wordCount);
    onClose();
  };

  console.log("", wordCount, wordLimitForLangDetection);
  if (wordCount > wordLimitForLangDetection) {
    let mostProbableLanguage;
    try {
      mostProbableLanguage = LanguageAbbreviations[lande(props.text)[0][0]];
    } catch (error) {
      mostProbableLanguage = "";
    }

    /*const mostProbableLanguage = lande(props.text);*/
    if (mostProbableLanguage !== currentLanguage) {
      setTimeout(() => {
        onOpen();
      }, 200);

      return (
        <>
          <Modal isOpen={isOpen} onClose={closeTemporaryIgnoreLanguageDetection} size="xl" scrollBehavior={"inside"}>
            {/* we kill the event here to disable drag and drop, since it is in the same container */}
            <ModalOverlay onMouseDown={killEvent}>
              <ModalContent alignItems="center">
                <ModalHeader>Switch Language?</ModalHeader>
                <ModalCloseButton />
                <ModalBody>
                  Do you want to switch language? The detected language is <b>{mostProbableLanguage}</b>, whereas your
                  chosen language is <b>{currentLanguage}</b>. The language can be changed on the top right.
                </ModalBody>
              </ModalContent>
            </ModalOverlay>
          </Modal>
        </>
      );
    }
  }

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

  return (
    <Stack direction={"column"}>
      <Textarea
        backgroundColor={backgroundColor}
        border="none"
        data-cy="reply"
        p="4"
        value={props.text}
        onChange={props.onTextChange}
        {...props.textareaProps}
      />
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
