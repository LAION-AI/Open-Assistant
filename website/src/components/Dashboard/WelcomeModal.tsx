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
} from "@chakra-ui/react";
import { useSession } from "next-auth/react";
import { useState } from "react";

export function WelcomeModal() {
  const { data: session } = useSession();

  const [showModal, setShowModal] = useState(true);

  if (!session) {
    return <></>;
  }
  if (session && session.user && session.user.isNew)
    return (
      <>
        <Modal isOpen={showModal} onClose={() => setShowModal(false)} isCentered>
          <ModalOverlay backdropFilter="auto" backdropBlur="2px" />
          <ModalContent borderRadius="xl">
            <Box p="6" pb="0">
              <ModalHeader>
                <Text
                  as="h1"
                  fontWeight="extrabold"
                  fontSize="3xl"
                  bgGradient="linear(320deg, #7162D4, #3182CE)"
                  bgClip="text"
                >
                  Welcome, {session.user.name || "Contributor"}!
                </Text>
              </ModalHeader>
              <ModalCloseButton mt="1" />
              <ModalBody mb="8">
                <Box>
                  <Text>
                    Open Assistant is an open-source AI assistant that uses and trains advanced language models to
                    understand and respond to humans.
                  </Text>
                  <Divider my="4" />
                  <Text>Complete tasks to help train the model and earn points.</Text>
                </Box>
              </ModalBody>
            </Box>
            <ModalFooter p="8">
              <Button colorScheme="blue" onClick={() => setShowModal(false)}>
                Got it!
              </Button>
            </ModalFooter>
          </ModalContent>
        </Modal>
      </>
    );
}
