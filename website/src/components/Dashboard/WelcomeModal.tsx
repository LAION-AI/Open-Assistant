import {
  Box,
  Button,
  Divider,
  Modal,
  ModalBody,
  ModalCloseButton,
  ModalContent,
  ModalFooter,
  ModalHeader,
  ModalOverlay,
  Text,
  useColorModeValue,
} from "@chakra-ui/react";
import { useSession } from "next-auth/react";
import { useState } from "react";

export function WelcomeModal() {
  const backgroundColor = useColorModeValue("white", "gray.700");
  const { data: session } = useSession();

  const [showModal, setShowModal] = useState(true);

  if (!session) {
    return <></>;
  }
  if (session && session.user)
    return (
      <>
        <Modal isOpen={showModal} onClose={() => setShowModal(false)} isCentered>
          <ModalOverlay backdropFilter="auto" backdropBlur="2px" />
          <ModalContent>
            <ModalHeader>Welcome, {session.user.name}!</ModalHeader>
            <ModalCloseButton />
            <ModalBody>
              <Box>
                <Text>
                  Open Assistant is an open-source AI assistant that uses and trains advanced language models to
                  understand and respond to humans.
                </Text>
                <Divider my="4" />
                <Text>Do tasks to help train the model and earn points based on the amount of tasks you do.</Text>
              </Box>
            </ModalBody>
            <ModalFooter>
              <Button colorScheme="blue" onClick={() => setShowModal(false)}>
                Got it!
              </Button>
            </ModalFooter>
          </ModalContent>
        </Modal>
      </>
    );
}
