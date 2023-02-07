import {} from "@chakra-ui/react";
import lande from "lande";
import { LanguageAbbreviations } from "src/lib/iso6393";
import React, { useEffect } from "react";
import {
  Progress,
  Stack,
  Textarea,
  TextareaProps,
  useColorModeValue,
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
  const backgroundColor = useColorModeValue("gray.100", "gray.900");
  const wordCount = (props.text.match(/\w+/g) || []).length;

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

export function getMostProbableLanguage(text: string) {
  let mostProbableLanguage;
  try {
    mostProbableLanguage = LanguageAbbreviations[lande(text)[0][0]];
  } catch (error) {
    mostProbableLanguage = "";
  }

  return mostProbableLanguage;
}

export function DifferentLanguageModal({ mostProbableLanguage, currentLanguage, setMostProbableLanguage }) {
  const { isOpen, onOpen, onClose } = useDisclosure();
  useEffect(() => {
    if (mostProbableLanguage !== currentLanguage) {
      onOpen();
    }
  }, []);

  return (
    <>
      <Modal
        isOpen={isOpen}
        onClose={() => {
          setMostProbableLanguage("");
          onClose();
        }}
        size="xl"
        scrollBehavior={"inside"}
      >
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
