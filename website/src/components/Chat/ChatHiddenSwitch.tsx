import { FormControl, FormLabel, Switch, SwitchProps } from "@chakra-ui/react";
import { useTranslation } from "next-i18next";
import { ChangeEvent, useCallback } from "react";

export const ChatHiddenSwitch = ({ onChange, value }: { onChange: (value: boolean) => void; value: boolean }) => {
  const { t } = useTranslation("chat");

  const onClick = useCallback(
    (event: ChangeEvent<HTMLInputElement>) => {
      onChange(event.target.checked);
    },
    [onChange]
  );

  return (
    <FormControl display="flex" alignItems="center" w="auto">
      <FormLabel htmlFor="show-hidden-chats-switch" mb="0">
        {t("show_hidden")}
      </FormLabel>
      <Switch id="show-hidden-chats-switch" isChecked={value} onChange={onClick} />
    </FormControl>
  );
};
