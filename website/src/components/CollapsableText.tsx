import {
  Button,
  Modal,
  ModalBody,
  ModalCloseButton,
  ModalContent,
  ModalHeader,
  ModalOverlay,
  useColorModeValue,
  useDisclosure,
} from "@chakra-ui/react";
import React, { ReactNode } from "react";

const killEvent = (e) => e.stopPropagation();

export const CollapsableText = ({
  text,
  maxLength = 220,
  isDisabled,
}: {
  text: ReactNode;
  maxLength?: number;
  isDisabled?: boolean;
}) => {
  const { isOpen, onOpen, onClose } = useDisclosure();

  const moreButtonColor = useColorModeValue("gray.600", "gray.400");

  if (typeof text !== "string" || text.length <= maxLength) {
    return <>{text}</>;
  } else {
    const text_with_breaks = text.split('\n').map((str, index) => <p key={index}>{str}</p>);
    return (
      <>
        <span>
          {text.substring(0, maxLength - 3)}&nbsp;
          <Button
            style={{ display: "inline" }}
            size={"xs"}
            variant={"solid"}
            bg={moreButtonColor}
            color={"white"}
            isDisabled={isDisabled}
            onClick={onOpen}
          >
            ...
          </Button>
        </span>
        <Modal isOpen={isOpen} onClose={onClose} size="xl" scrollBehavior={"inside"}>
          {/* we kill the event here to disable drag and drop, since it is in the same container */}
          <ModalOverlay onMouseDown={killEvent}>
            <ModalContent alignItems="center">
              <ModalHeader>Full Text</ModalHeader>
              <ModalCloseButton />
              <ModalBody>{text_with_breaks}</ModalBody>
            </ModalContent>
          </ModalOverlay>
        </Modal>
      </>
    );
  }
};
