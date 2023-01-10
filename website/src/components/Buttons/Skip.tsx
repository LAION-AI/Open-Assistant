import {
  Button,
  ButtonProps,
  Modal,
  ModalBody,
  ModalCloseButton,
  ModalContent,
  ModalFooter,
  ModalHeader,
  ModalOverlay,
  Textarea,
  useDisclosure,
} from "@chakra-ui/react";
import { useState } from "react";

interface SkipButtonProps extends ButtonProps {
  onSkip: (reason: string) => void;
}

export const SkipButton = ({ onSkip, ...props }: SkipButtonProps) => {
  const { isOpen, onOpen: showModal, onClose: closeModal } = useDisclosure();
  const [value, setValue] = useState("");

  const onSubmit = () => {
    onSkip(value);
    setValue("");
    closeModal();
  };

  return (
    <>
      <Button size="lg" variant="outline" onClick={showModal} {...props}>
        Skip
      </Button>
      <Modal isOpen={isOpen} onClose={closeModal}>
        <ModalOverlay />
        <ModalContent>
          <ModalHeader>Skip</ModalHeader>
          <ModalCloseButton />
          <ModalBody>
            <Textarea
              value={value}
              onChange={(e) => setValue(e.target.value)}
              resize="none"
              placeholder="Any feedback on this task?"
            />
          </ModalBody>

          <ModalFooter>
            <Button colorScheme="blue" mr={3} onClick={onSubmit}>
              Send
            </Button>
          </ModalFooter>
        </ModalContent>
      </Modal>
    </>
  );
};
