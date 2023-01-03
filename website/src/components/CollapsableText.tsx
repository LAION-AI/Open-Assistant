import { Button, useDisclosure } from "@chakra-ui/react";
import { Modal, ModalOverlay, ModalContent, ModalHeader, ModalBody, ModalCloseButton } from "@chakra-ui/react";
import React from "react";

export const CollapsableText = ({ text, maxLength = 220 }) => {
  const { isOpen, onOpen, onClose } = useDisclosure();
  if (typeof text != "string" || text.length <= maxLength) {
    return text;
  } else {
    return (
      <>
        {text.substring(0, maxLength - 3)}
        <Button style={{ display: "contents" }} onClick={onOpen}>
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
