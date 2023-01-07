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
  useDisclosure,
} from "@chakra-ui/react";
import { TaskControls, TaskControlsProps } from "src/components/Survey/TaskControls";

interface TaskControlsOverridableProps extends TaskControlsProps {
  isValid: boolean;
  prepareForSubmit: () => void;
}

export const TaskControlsOverridable = (props: TaskControlsOverridableProps) => {
  const { isValid, onSubmitResponse, ...rest } = props;
  const { isOpen: isModalOpen, onOpen: onOpenModal, onClose: onModalClose } = useDisclosure();

  const unchangedResponsePrompt = () => {
    onOpenModal();

    // Ideally this happens when the user clicks submit, but we can't
    // reliably wait for it to be executed before submitting the response
    // without significant refactoring.
    // As a result, modal will only display once even if the user doesn't proceed
    props.prepareForSubmit();
  };

  const onSubmitResponseOverride = () => {
    onSubmitResponse(props.tasks[0]);
    onModalClose();
  };

  return (
    <>
      <Modal isOpen={isModalOpen} onClose={onModalClose} isCentered>
        <ModalOverlay />
        <ModalContent>
          <ModalCloseButton />
          <ModalHeader>Order Unchanged</ModalHeader>
          <ModalBody>You have not changed the order of the prompts. Are you sure you would like to submit?</ModalBody>
          <ModalFooter>
            <Flex justify="center" ml="auto" gap={2}>
              <Button variant={"ghost"} onClick={onModalClose}>
                Cancel
              </Button>
              <Button onClick={onSubmitResponseOverride}>Submit anyway</Button>
            </Flex>
          </ModalFooter>
        </ModalContent>
      </Modal>
      <TaskControls onSubmitResponse={isValid ? props.onSubmitResponse : unchangedResponsePrompt} {...rest} />
    </>
  );
};
