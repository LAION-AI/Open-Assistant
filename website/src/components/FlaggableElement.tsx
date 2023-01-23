import {
  Box,
  Button,
  Modal,
  ModalBody,
  ModalCloseButton,
  ModalContent,
  ModalFooter,
  ModalHeader,
  ModalOverlay,
  Popover,
  PopoverAnchor,
  PopoverTrigger,
  Tooltip,
  useColorModeValue,
  useDisclosure,
} from "@chakra-ui/react";
import { AlertCircle } from "lucide-react";
import { useState } from "react";
import { get, post } from "src/lib/api";
import { colors } from "src/styles/Theme/colors";
import { Message } from "src/types/Conversation";
import useSWRImmutable from "swr/immutable";
import useSWRMutation from "swr/mutation";

import { LabelInputGroup } from "./Survey/LabelInputGroup";

interface Label {
  name: string;
  display_text: string;
  help_text: string;
}

interface FlaggableElementProps {
  children: React.ReactNode;
  message: Message;
}

interface ValidLabelsResponse {
  valid_labels: Label[];
}

export const FlaggableElement = (props: FlaggableElementProps) => {
  const { data: response } = useSWRImmutable<ValidLabelsResponse>("/api/valid_labels", get);
  const { isOpen, onOpen, onClose } = useDisclosure();
  const { valid_labels } = response || { valid_labels: [] };
  const [values, setValues] = useState<number[]>([]);

  const submittable =
    values.some((value) => {
      return value !== null;
    }) &&
    values.length === valid_labels.length &&
    valid_labels.length > 0;

  const { trigger } = useSWRMutation("/api/set_label", post, {
    onSuccess: onClose,
    onError: onClose,
  });

  const submitResponse = () => {
    const label_map: Map<string, number> = new Map();
    console.assert(valid_labels.length === values.length);
    values.forEach((value, idx) => {
      if (value !== null) {
        label_map.set(valid_labels[idx].name, value);
      }
    });
    trigger({
      message_id: props.message.id,
      label_map: Object.fromEntries(label_map),
      text: props.message.text,
    });
  };

  return (
    <Popover isOpen={isOpen} onOpen={onOpen} onClose={onClose} closeOnBlur={false} isLazy lazyBehavior="keepMounted">
      <Box display="flex" alignItems="center" flexDirection={["column", "row"]} gap="2">
        <PopoverAnchor>{props.children}</PopoverAnchor>

        <Tooltip label="Report" bg="red.500" aria-label="A tooltip">
          <Box>
            <PopoverTrigger>
              <Box as="button" display="flex" alignItems="center" justifyContent="center" borderRadius="full" p="1">
                <AlertCircle size="20" className="text-red-400" aria-hidden="true" />
              </Box>
            </PopoverTrigger>
          </Box>
        </Tooltip>
      </Box>

      <Modal isOpen={isOpen} onClose={onClose}>
        <ModalOverlay />
        <ModalContent>
          <ModalHeader>Select one or more labels that apply.</ModalHeader>
          <ModalCloseButton />
          <ModalBody>
            <LabelInputGroup simple labelIDs={valid_labels.map(({ name }) => name)} onChange={setValues} />
          </ModalBody>
          <ModalFooter>
            <Button
              isDisabled={!submittable}
              onClick={submitResponse}
              className={`bg-indigo-600 text-${useColorModeValue(
                colors.light.text,
                colors.dark.text
              )} hover:bg-indigo-700`}
            >
              Report
            </Button>
          </ModalFooter>
        </ModalContent>
      </Modal>
    </Popover>
  );
};
