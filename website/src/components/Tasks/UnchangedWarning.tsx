import {
  Button,
  Flex,
  Modal,
  ModalBody,
  ModalCloseButton,
  ModalContent,
  ModalFooter,
  ModalHeader,
  ModalOverlay,
} from "@chakra-ui/react";

interface UnchangedWarningProps {
  show: boolean;
  title: string;
  message: string;
  continueButtonText: string;
  onClose: () => void;
  onContinueAnyway: () => void;
}

export const UnchangedWarning = (props: UnchangedWarningProps) => {
  return (
    <>
      <Modal isOpen={props.show} onClose={props.onClose} isCentered>
        <ModalOverlay />
        <ModalContent>
          <ModalCloseButton />
          <ModalHeader>{props.title}</ModalHeader>
          <ModalBody>{props.message}</ModalBody>
          <ModalFooter>
            <Flex justify="center" ml="auto" gap={2}>
              <Button variant={"ghost"} onClick={props.onClose}>
                Cancel
              </Button>
              <Button onClick={props.onContinueAnyway}>{props.continueButtonText}</Button>
            </Flex>
          </ModalFooter>
        </ModalContent>
      </Modal>
    </>
  );
};
