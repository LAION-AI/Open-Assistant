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
import { useTranslation } from "next-i18next";
import { useState } from "react";

interface SkipButtonProps extends ButtonProps {
  onSkip: (reason: string) => void;
}

export const SkipButton = ({ onSkip, ...props }: SkipButtonProps) => {
  const { t } = useTranslation(["common", "tasks"]);
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
        {t("skip")}
      </Button>
      <Modal isOpen={isOpen} onClose={closeModal}>
        <ModalOverlay />
        <ModalContent>
          <ModalHeader>{t("skip")}</ModalHeader>
          <ModalCloseButton />
          <ModalBody>
            <Textarea
              value={value}
              onChange={(e) => setValue(e.target.value)}
              resize="none"
              placeholder={t("tasks:any_feedback_on_this_task")}
            />
          </ModalBody>

          <ModalFooter>
            <Button colorScheme="blue" mr={3} onClick={onSubmit}>
              {t("send")}
            </Button>
          </ModalFooter>
        </ModalContent>
      </Modal>
    </>
  );
};
