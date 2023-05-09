import { Grid, Text } from "@chakra-ui/react";
import { useTranslation } from "next-i18next";
import React from "react";
import { useFormContext } from "react-hook-form";
import { ChatConfigFormData } from "src/types/Chat";

export default function ChatConfigSummary() {
  const { t } = useTranslation("chat");
  const { watch } = useFormContext<ChatConfigFormData>();
  const config = watch();
  return (
    <Grid gridTemplateColumns="repeat(2, max-content)" columnGap={4} fontSize="sm">
      <Text>{t("model")}</Text>
      <Text>{config["model_config_name"]}</Text>
      {Object.entries(config)
        .filter(([key, value]) => key !== "model_config_name" && key !== "plugins" && value !== null)
        .map(([key, value]) => (
          <React.Fragment key={key}>
            <Text>{t(key as any)}</Text>
            <Text>{value}</Text>
          </React.Fragment>
        ))}
    </Grid>
  );
}
