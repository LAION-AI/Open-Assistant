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
  useDisclosure,
} from "@chakra-ui/react";
import { useTranslation } from "next-i18next";

interface SkipButtonProps extends ButtonProps {
  onSkip: () => void;
  confirmSkip: boolean;
}

export const SkipButton = ({ ...props }: SkipButtonProps) => {
  const { t } = useTranslation();
  const { isOpen, onOpen: showModal, onClose: closeModal } = useDisclosure();

  const onClick = () => {
    if (props.confirmSkip) {
      showModal();
    } else {
      props.onSkip();
    }
  };

  const onConfirmedSkip = () => {
    closeModal();
    props.onSkip();
  };

  return (
    <>
      <Button size="lg" variant="solid" {...props} onClick={onClick}>
        {t("skip")}
      </Button>
      <Modal isOpen={isOpen} onClose={closeModal}>
        <ModalOverlay></ModalOverlay>
        <ModalContent>
          <ModalCloseButton></ModalCloseButton>
          <ModalHeader>{t("skip")}</ModalHeader>
          <ModalBody>
            <div>{t("tasks:skip_confirmation")}</div>
          </ModalBody>
          <ModalFooter>
            <Button mr={3} onClick={onConfirmedSkip}>
              {t("yes")}
            </Button>
            <Button colorScheme="blue" onClick={closeModal}>
              {t("no")}
            </Button>
          </ModalFooter>
        </ModalContent>
      </Modal>
    </>
  );
};
