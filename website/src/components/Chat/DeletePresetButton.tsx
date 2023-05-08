import { Button } from "@chakra-ui/react";
import { useTranslation } from "next-i18next";

export const DeletePresetButton = ({ onClick }: { onClick: () => void }) => {
  const { t } = useTranslation();

  return (
    <Button onClick={onClick} py="3" variant="outline" colorScheme="red" w="full">
      {t("delete")}
    </Button>
  );
};
