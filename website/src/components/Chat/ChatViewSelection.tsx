import { Select, SelectProps } from "@chakra-ui/react";
import { useTranslation } from "next-i18next";

export const ChatViewSelection = (props: SelectProps) => {
  const { t } = useTranslation("chat");

  return (
    <Select {...props}>
      <option value="visible">{t("only_visible")}</option>
      <option value="visible_hidden">{t("visible_hidden")}</option>
    </Select>
  );
};
