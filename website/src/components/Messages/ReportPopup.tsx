import {
  Button,
  Modal,
  ModalBody,
  ModalCloseButton,
  ModalContent,
  ModalFooter,
  ModalHeader,
  ModalOverlay,
  Textarea,
} from "@chakra-ui/react";
import { useState } from "react";
import { post } from "src/lib/api";
import useSWRMutation from "swr/mutation";

interface ReportPopupProps {
  messageId: string;
  show: boolean;
  onClose: () => void;
}

export const ReportPopup = ({ messageId, show, onClose }: ReportPopupProps) => {
  const [text, setText] = useState("");
  const { trigger } = useSWRMutation("/api/report", post);

  const submit = () => {
    trigger({
      message_id: messageId,
      text,
    });

    setText("");
    onClose();
  };

  return (
    <Modal isOpen={show} onClose={onClose}>
      <ModalOverlay />
      <ModalContent>
        <ModalHeader>Report</ModalHeader>
        <ModalCloseButton />
        <ModalBody>
          <Textarea
            onChange={(e) => setText(e.target.value)}
            resize="none"
            placeholder="Why should this message be reviewed?"
          />
        </ModalBody>

        <ModalFooter>
          <Button colorScheme="blue" mr={3} onClick={submit}>
            Send
          </Button>
        </ModalFooter>
      </ModalContent>
    </Modal>
  );
};
