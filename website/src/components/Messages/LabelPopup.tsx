import {
  Button,
  Modal,
  ModalBody,
  ModalCloseButton,
  ModalContent,
  ModalFooter,
  ModalHeader,
  ModalOverlay,
} from "@chakra-ui/react";
import { useTranslation } from "next-i18next";
import { useState } from "react";
import { LabelInputGroup } from "src/components/Survey/LabelInputGroup";
import { get, post } from "src/lib/api";
import useSWRImmutable from "swr/immutable";
import useSWRMutation from "swr/mutation";

interface LabelMessagePopupProps {
  messageId: string;
  show: boolean;
  onClose: () => void;
}

interface Label {
  name: string;
  display_text: string;
  help_text: string;
}

interface ValidLabelsResponse {
  valid_labels: Label[];
}

export const LabelMessagePopup = ({ messageId, show, onClose }: LabelMessagePopupProps) => {
  const { t } = useTranslation("message");
  const { data: response } = useSWRImmutable<ValidLabelsResponse>("/api/valid_labels", get);
  const { valid_labels } = response || { valid_labels: [] };
  const [values, setValues] = useState<number[]>(null);

  const { trigger } = useSWRMutation("/api/set_label", post);

  const submit = () => {
    const label_map: Map<string, number> = new Map();
    console.assert(valid_labels.length === values.length);
    values.forEach((value, idx) => {
      if (value !== null) {
        label_map.set(valid_labels[idx].name, value);
      }
    });
    trigger({
      message_id: messageId,
      label_map: Object.fromEntries(label_map),
    });

    setValues(null);
    onClose();
  };

  return (
    <Modal isOpen={show} onClose={onClose}>
      <ModalOverlay />
      <ModalContent>
        <ModalHeader>{t("label_title")}Label</ModalHeader>
        <ModalCloseButton />
        <ModalBody>
          <LabelInputGroup labelIDs={valid_labels.map(({ name }) => name)} onChange={setValues} />
        </ModalBody>
        <ModalFooter>
          <Button colorScheme="blue" mr={3} onClick={submit}>
            {t("submit_labels")}
          </Button>
        </ModalFooter>
      </ModalContent>
    </Modal>
  );
};
