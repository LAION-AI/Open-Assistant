import { Box } from "@chakra-ui/react";
import { useTranslation } from "next-i18next";
import { memo } from "react";

export const ChatWarning = memo(function ChatWarning() {
  const { t } = useTranslation("chat");
  return (
    <Box fontSize={["xs", "sm"]} textAlign="center" mb="2" className="max-w-5xl mx-auto">
      {t("warning")}
    </Box>
  );
});
