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
import { useState, useEffect } from "react";

export function WelcomeModal() {
  const backgroundColor = useColorModeValue("white", "gray.700");
  const { data: session } = useSession();

  const [showModal, setShowModal] = useState(true);

  //   useEffect(() => {
  //     if (!localStorage.getItem("welcomeModalSeen")) {
  //       setShowModal(true);
  //       localStorage.setItem("welcomeModalSeen", "true");
  //     } else {
  //       setShowModal(false);
  //     }
  //   }, []);

  if (!session) {
    return <></>;
  }
  if (session && session.user)
    return (
      <>
        <Modal isOpen={showModal} onClose={() => setShowModal(false)} isCentered>
          <ModalOverlay backdropFilter="auto" backdropBlur="2px" />
          <ModalContent>
            <ModalHeader>Welcome, {session.user.name || "Contributor"}!</ModalHeader>
            <ModalCloseButton />
            <ModalBody>
              <Box>
                <Text>
                  Open Assistant is an open-source AI assistant that uses and trains advanced language models to
                  understand and respond to humans.
                </Text>
                <Divider my="4" />
                <Text>Complete tasks to help train the model and earn points!</Text>
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
