import React, { useState } from "react";
import {
  Button,
  Modal,
  ModalOverlay,
  ModalContent,
  ModalHeader,
  ModalBody,
  ModalFooter,
  FormControl,
  FormLabel,
  Input,
  Text,
  Textarea,
} from "@chakra-ui/react";
import { BookOpen } from "lucide-react";
import { useTranslation } from "next-i18next";
import { CustomInstructionsType } from "src/types/Chat";

const CHAR_LIMIT = 256;

const CustomInstructions = ({ onChange, savedCustomInstructions }) => {
  const [isOpen, setIsOpen] = useState(false);
  const [customInstructions, setCustomInstructions] = useState<CustomInstructionsType>({
    user_profile: "",
    user_response_instructions: "",
  });
  const { t } = useTranslation("chat");

  const handleOpen = () => {
    setCustomInstructions(savedCustomInstructions);
    setIsOpen(true);
  };
  const handleClose = () => setIsOpen(false);
  const handleSave = () => {
    setIsOpen(false);
    onChange(customInstructions);
  };

  function createChangeHandler(key: string) {
    return function handleInputChange(event: React.ChangeEvent<HTMLTextAreaElement>) {
      const { value } = event.target;
      if (value.length <= CHAR_LIMIT) {
        setCustomInstructions((prevInstructions) => ({
          ...prevInstructions,
          [key]: value,
        }));
      }
    };
  }

  const handleUserProfileChange = createChangeHandler("user_profile");
  const handleUserResponseInstructionsChange = createChangeHandler("user_response_instructions");

  return (
    <>
      <Button leftIcon={<BookOpen />} onClick={handleOpen}>
        {t("custom_instructions")}
      </Button>

      <Modal isOpen={isOpen} onClose={handleClose} size="xl">
        <ModalOverlay />
        <ModalContent>
          <ModalHeader>{t("custom_instructions")}</ModalHeader>
          <ModalBody>
            <FormControl>
              <FormLabel>{t("custom_instructions_user_profile")}</FormLabel>
              <Textarea
                rows={6}
                resize="none"
                height="auto"
                value={customInstructions?.user_profile}
                onChange={handleUserProfileChange}
                placeholder={t("custom_instructions_user_profile_placeholder")}
              />
              <Text fontSize="sm">{`${customInstructions?.user_profile?.length}/${CHAR_LIMIT}`}</Text>
            </FormControl>
            <FormControl mt={4}>
              <FormLabel>{t("custom_instructions_response_instructions")}</FormLabel>
              <Textarea
                rows={6}
                height="auto"
                resize="none"
                value={customInstructions?.user_response_instructions}
                onChange={handleUserResponseInstructionsChange}
                placeholder={t("custom_instructions_response_instructions_placeholder")}
              />
              <Text fontSize="sm">{`${customInstructions?.user_response_instructions?.length}/${CHAR_LIMIT}`}</Text>
            </FormControl>
          </ModalBody>

          <ModalFooter>
            <Button colorScheme="blue" mr={3} onClick={handleSave}>
              Save
            </Button>
            <Button variant="ghost" onClick={handleClose}>
              Cancel
            </Button>
          </ModalFooter>
        </ModalContent>
      </Modal>
    </>
  );
};

export default CustomInstructions;
