import { Box, Button, Flex, IconButton, Input, useBoolean, useToast } from "@chakra-ui/react";
import { Check, X } from "lucide-react";
import { useTranslation } from "next-i18next";
import { KeyboardEvent, useCallback, useRef } from "react";
import { CustomPreset } from "src/utils/chat";

import { toCustomPresetName } from "./ChatConfigForm";

export const SavePresetButton = ({
  customPresets,
  onSave,
}: {
  customPresets: CustomPreset[];
  onSave: (name: string) => void;
}) => {
  const [isSaving, setIsSaving] = useBoolean();
  const { t } = useTranslation();
  const inputRef = useRef<HTMLInputElement>(null);
  const toast = useToast();
  const handleSave = useCallback(() => {
    const name = inputRef.current?.value.trim();
    if (!name) {
      return;
    }

    const isExists = customPresets.findIndex((preset) => preset.name === toCustomPresetName(name)) !== -1;

    if (isExists) {
      toast({
        title: t("chat:preset_exists_error"),
        status: "error",
      });
    } else {
      onSave(name);
      setIsSaving.off();
    }
  }, [customPresets, onSave, setIsSaving, t, toast]);

  const handleKeyDown = useCallback(
    (e: KeyboardEvent) => {
      if (e.key === "Escape") {
        setIsSaving.off();
      }
      if (e.key === "Enter") {
        handleSave();
      }
    },
    [handleSave, setIsSaving]
  );

  return (
    <Box pe="4" position="relative">
      {!isSaving ? (
        <Button onClick={setIsSaving.on} py="3" variant="outline" colorScheme="blue" w="full">
          {t("chat:save_preset")}
        </Button>
      ) : (
        <>
          <Input
            py="3"
            pe="56px"
            ref={inputRef}
            onKeyDown={handleKeyDown}
            autoFocus
            placeholder={t("chat:preset_name_placeholder")}
          ></Input>
          <Flex position="absolute" top="2" className="ltr:right-6 rtl:left-6" gap="1" zIndex="10">
            <IconButton
              size="xs"
              variant="ghost"
              icon={<Check size="16px" />}
              aria-label={t("save")}
              onClick={handleSave}
            ></IconButton>
            <IconButton
              size="xs"
              variant="ghost"
              icon={<X size="16px" />}
              aria-label={t("cancel")}
              onClick={setIsSaving.off}
            ></IconButton>
          </Flex>
        </>
      )}
    </Box>
  );
};
