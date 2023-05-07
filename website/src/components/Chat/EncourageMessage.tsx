import { Badge } from "@chakra-ui/react";
import { useTranslation } from "next-i18next";
// kept brief so that it doesnt distract/interfere with user experience
export const EncourageMessage = () => {
  const { t } = useTranslation("chat");
  return (
    <Badge fontWeight="normal" background="gray.300" color="black">
      {t("feedback_message")}
    </Badge>
  );
};
