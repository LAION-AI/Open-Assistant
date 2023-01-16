import { Box, Button, Divider, Text, useColorMode } from "@chakra-ui/react";
import { useSession } from "next-auth/react";
import { useState } from "react";
import { FiX } from "react-icons/fi";

export function WelcomeCard() {
  const { colorMode } = useColorMode();
  const backgroundColor = colorMode === "light" ? "white" : "gray.700";
  const titleColor = colorMode === "light" ? "blue.500" : "blue.300";

  const { data: session } = useSession();

  const [showCard, setShowCard] = useState("true");

  if (!session) {
    return <></>;
  }
  if (session && session.user && session.user.isNew)
    return (
      <>
        <Box
          bgGradient="linear(to-r, blue.300, purple.500)"
          borderRadius="xl"
          display={showCard}
          p="1px"
          shadow="base"
          position="relative"
        >
          <Box bg={backgroundColor} borderRadius="xl" p="6" pt="4" pr="12">
            <Box pb="2">
              <Text as="h1" fontWeight="extrabold" fontSize="3xl" color={titleColor}>
                Welcome, {session.user.name || "Contributor"}!
              </Text>
            </Box>

            <Box>
              <Text>
                Open Assistant is an open-source AI assistant that uses and trains advanced language models to
                understand and respond to humans.
              </Text>
              <Divider my="4" />
              <Text>Complete tasks to help train the model and earn points.</Text>
            </Box>

            <Button position="absolute" top="2" right="2" p="0" size="sm" onClick={() => setShowCard("none")}>
              <FiX />
            </Button>
          </Box>
        </Box>
      </>
    );
}
