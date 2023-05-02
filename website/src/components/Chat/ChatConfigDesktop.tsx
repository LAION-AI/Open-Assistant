import { Box } from "@chakra-ui/react";
import { useTranslation } from "next-i18next";
import { memo } from "react";
import SimpleBar from "simplebar-react";

import { ChatConfigForm } from "./ChatConfigForm";

export const ChatConfigDesktop = memo(function ChatConfigDesktop() {
  const { t } = useTranslation("chat");
  return (
    <Box
      py="4"
      pl="4"
      gap="1"
      height="full"
      minH="0"
      flexDirection="column"
      w="270px"
      display={{ base: "none", xl: "flex" }}
      _dark={{
        bg: "blackAlpha.400",
      }}
    >
      <Box fontSize="xl" borderBottomWidth="1px" mb="4" pb="4">
        {t("config_title")}
      </Box>

      <SimpleBar
        style={{ maxHeight: "100%", height: "100%", minHeight: "0" }}
        classNames={{
          contentEl: "mr-4 flex flex-col overflow-y-auto items-center",
        }}
      >
        <ChatConfigForm />
      </SimpleBar>
    </Box>
  );
});
