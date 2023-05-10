import { Box } from "@chakra-ui/react";
import { useTranslation } from "next-i18next";
import { memo, ReactNode } from "react";

export const ChatConfigDesktop = memo(function ChatConfigDesktop({ children }: { children: ReactNode }) {
  const { t } = useTranslation("chat");
  return (
    <Box
      py="4"
      pl="4"
      gap="1"
      height="full"
      minH="0"
      flexDirection="column"
      minW="270px"
      maxW="270px"
      display={{ base: "none", xl: "flex" }}
      _dark={{
        bg: "blackAlpha.400",
      }}
    >
      <Box fontSize="xl" borderBottomWidth="1px" mb="4" pb="4">
        {t("config_title")}
      </Box>
      {children}
    </Box>
  );
});
