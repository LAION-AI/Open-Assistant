import { Box } from "@chakra-ui/react";
import { useTranslation } from "next-i18next";

export const ChatWarning = () => {
  const { t } = useTranslation("chat");
  return (
    <Box fontSize="sm" textAlign="center" mb="2" className="max-w-5xl mx-auto">
      {t("warning")}
    </Box>
  );
};
