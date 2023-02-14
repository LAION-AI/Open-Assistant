import { Box, Divider, Text, useColorMode } from "@chakra-ui/react";
import { useSession } from "next-auth/react";
import { useTranslation } from "next-i18next";

export function WelcomeCard() {
  const { colorMode } = useColorMode();
  const backgroundColor = colorMode === "light" ? "white" : "gray.700";
  const titleColor = colorMode === "light" ? "blue.500" : "blue.300";

  const { data: session } = useSession();
  const { t } = useTranslation("dashboard");

  if (!session) {
    return <></>;
  }
  if (session && session.user && session.user.isNew)
    return (
      <>
        <Box
          bgGradient="linear(to-r, blue.300, purple.500)"
          borderRadius="xl"
          p="1px"
          shadow="base"
          position="relative"
        >
          <Box bg={backgroundColor} borderRadius="xl" p="6" pt="4" pr="12">
            <Box pb="2">
              <Text as="h1" fontWeight="extrabold" fontSize="3xl" color={titleColor}>
                {t("welcome_message.label", { username: session.user.name || t("welcome_message.contributor") })}
              </Text>
            </Box>
            <Box>
              <Text>{t("welcome_message.description")}</Text>
              <Divider my="4" />
              <Text>{t("welcome_message.instruction")}</Text>
            </Box>
          </Box>
        </Box>
      </>
    );
}
