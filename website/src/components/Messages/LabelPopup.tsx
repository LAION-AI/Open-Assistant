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
import { useCallback, useEffect, useMemo, useState } from "react";
import { LabelInputGroup } from "src/components/Messages/LabelInputGroup";
import { get, post } from "src/lib/api";
import { Message } from "src/types/Conversation";
import { Label } from "src/types/Tasks";
import useSWRImmutable from "swr/immutable";
import useSWRMutation from "swr/mutation";

interface LabelMessagePopupProps {
  message: Message;
  show: boolean;
  onClose: () => void;
}

interface ValidLabelsResponse {
  valid_labels: Label[];
}

export const LabelMessagePopup = ({ message, show, onClose }: LabelMessagePopupProps) => {
  const { t } = useTranslation();
  const { data: response } = useSWRImmutable<ValidLabelsResponse>(`/api/valid_labels?message_id=${message.id}`, get);
  const valid_labels = useMemo(() => response?.valid_labels ?? [], [response]);
  const [values, setValues] = useState<number[]>(new Array(valid_labels.length).fill(null));

  useEffect(() => {
    setValues(new Array(valid_labels.length).fill(null));
  }, [message.id, valid_labels.length]);

  const { trigger: setLabels } = useSWRMutation("/api/set_label", post);

  const submit = useCallback(() => {
    const label_map: Map<string, number> = new Map();
    console.assert(valid_labels.length === values.length);
    values.forEach((value, idx) => {
      if (value !== null) {
        label_map.set(valid_labels[idx].name, value);
      }
    });
    setLabels({
      message_id: message.id,
      label_map: Object.fromEntries(label_map),
    });

    setValues(new Array(values.length).fill(null));
    onClose();
  }, [message.id, onClose, setLabels, valid_labels, values]);

  return (
    <Modal isOpen={show} onClose={onClose}>
      <ModalOverlay />
      <ModalContent>
        <ModalHeader>{t("message:label_title")}</ModalHeader>
        <ModalCloseButton />
        <ModalBody>
          <LabelInputGroup
            labels={valid_labels}
            values={values}
            instructions={{
              yesNoInstruction: t("labelling:label_message_yes_no_instruction"),
              flagInstruction: t("labelling:label_message_flag_instruction"),
              likertInstruction: t("labelling:label_message_likert_instruction"),
            }}
            expectedLanguage={message.lang}
            onChange={setValues}
          />
        </ModalBody>
        <ModalFooter>
          <Button colorScheme="blue" mr={3} onClick={submit}>
            {t("message:submit_labels")}
          </Button>
        </ModalFooter>
      </ModalContent>
    </Modal>
  );
};
