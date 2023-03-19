import { Badge, Tooltip } from "@chakra-ui/react";
import { useTranslation } from "next-i18next";

export const MessageSyntheticBadge = () => {
  const { t } = useTranslation("message");

  return (
    <Tooltip label={t("synthetic_explain")} placement="top" hasArrow>
      <Badge size="sm" colorScheme="green" textTransform="capitalize">
        {t("synthetic")}
      </Badge>
    </Tooltip>
  );
};
