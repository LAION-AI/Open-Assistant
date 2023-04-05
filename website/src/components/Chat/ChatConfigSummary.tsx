import { Grid, Text } from "@chakra-ui/react";
import { useTranslation } from "next-i18next";
import React from "react";
import { useFormContext } from "react-hook-form";
import { ChatConfigForm } from "src/types/Chat";

export const ChatConfigSummary = () => {
  const { watch } = useFormContext<ChatConfigForm>();
  const { t } = useTranslation("chat");

  const values = watch();
  const { model_config_name } = values;

  return (
    <Grid gridTemplateColumns="repeat(2, max-content)" columnGap={4} fontSize="sm">
      <Text>{t("model")}</Text>
      <Text>{model_config_name}</Text>
      {Object.keys(values)
        .filter((key) => key !== "model_config_name" && values[key] !== null)
        .map((key) => (
          <React.Fragment key={key}>
            <Text>{t(key as any)}</Text>
            <Text>{values[key]}</Text>
          </React.Fragment>
        ))}
    </Grid>
  );
};
