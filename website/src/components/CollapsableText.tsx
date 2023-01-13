import {
  Button,
  Modal,
  ModalBody,
  ModalCloseButton,
  ModalContent,
  ModalHeader,
  ModalOverlay,
  useDisclosure,
} from "@chakra-ui/react";
import React, { ReactNode } from "react";

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

  if (typeof text !== "string" || text.length <= maxLength) {
    return <>{text}</>;
  } else {
    return (
      <>
        {text.substring(0, maxLength - 3)}
        <Button style={{ display: "contents" }} isDisabled={isDisabled} onClick={onOpen}>
          ...
        </Button>
        <Modal isOpen={isOpen} onClose={onClose} size="xl" scrollBehavior={"inside"}>
          <ModalOverlay style={{ width: "100%", height: "100%" }}>
            <ModalContent maxH="400">
              <ModalHeader>Full Text</ModalHeader>
              <ModalCloseButton />
              <ModalBody>{text}</ModalBody>
            </ModalContent>
          </ModalOverlay>
        </Modal>
      </>
    );
  }
};
