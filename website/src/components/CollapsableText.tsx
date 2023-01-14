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
