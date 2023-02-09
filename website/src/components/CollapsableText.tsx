import {
  Button,
  Modal,
  ModalBody,
  ModalCloseButton,
  ModalContent,
  ModalHeader,
  ModalOverlay,
  Tooltip,
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
  const finalRef = React.useRef(null);

  const moreButtonColor = useColorModeValue("gray.600", "gray.400");

  if (typeof text !== "string" || text.length <= maxLength) {
    return <>{text}</>;
  } else {
    return (
      <>
        <span ref={finalRef}>
          {text.substring(0, maxLength - 3)}&nbsp;
          <Tooltip label={text} maxW="70vw">
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
          </Tooltip>
        </span>
        <Modal
          finalFocusRef={finalRef}
          isOpen={isOpen}
          onClose={onClose}
          size="xl"
          scrollBehavior={"inside"}
          isCentered
        >
          {/* we kill the event here to disable drag and drop, since it is in the same container */}
          <ModalOverlay onMouseDown={killEvent}>
            <ModalContent pb={5} alignItems="center">
              <ModalHeader>Full Text</ModalHeader>
              <ModalCloseButton />
              <ModalBody whiteSpace="pre-line">{text}</ModalBody>
            </ModalContent>
          </ModalOverlay>
        </Modal>
      </>
    );
  }
};
