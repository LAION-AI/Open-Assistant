import {
  Button,
  Text,
  Tooltip,
  Radio,
  RadioGroup,
  Box,
  Editable,
  EditableInput,
  EditablePreview,
  Image,
  FormControl,
  FormLabel,
  Icon,
  IconButton,
  Menu,
  MenuButton,
  MenuItem,
  MenuList,
  Modal,
  ModalBody,
  ModalCloseButton,
  ModalContent,
  ModalFooter,
  ModalHeader,
  ModalOverlay,
  Stack,
  Textarea,
  useDisclosure,
} from "@chakra-ui/react";
import { Cog, Edit, Plus } from "lucide-react";
import { AttachmentIcon, WarningIcon, CheckCircleIcon, CloseIcon } from "@chakra-ui/icons";
import { ChangeEvent, useCallback, useMemo, useEffect, useState, useRef } from "react";
import { useTranslation } from "next-i18next";
import { Controller, useFormContext } from "react-hook-form";
import { ChatConfigFormData } from "src/types/Chat";
import { useChatContext } from "./ChatContext";
import { PluginEntry } from "src/types/Chat";
import { get, post } from "src/lib/api";
import { API_ROUTES } from "src/lib/routes";

export const PluginsChooser = ({ plugins }: { plugins: PluginEntry[] }) => {
  const { t } = useTranslation("chat");
  const { control, register, reset, setValue } = useFormContext<ChatConfigFormData>();
  const [selectedForEditPluginIndex, setSelectedForEditPluginIndex] = useState<number | null>(null);
  const { isOpen, onOpen, onClose } = useDisclosure();

  const textareaRef = useRef<HTMLTextAreaElement | null>(null);
  const containerRef = useRef<HTMLDivElement | null>(null);

  const activePluginIndex = useMemo(() => {
    return plugins.findIndex((plugin) => plugin.enabled);
  }, [plugins]);

  const handlePluginSelect = useCallback(
    (index: number) => {
      const selectedIndex = plugins.findIndex((plugin) => plugin.enabled);
      const newPlugins = plugins.map((plugin, i) => ({
        ...plugin,
        enabled: selectedIndex === index ? false : i === index,
      }));
      setValue("plugins", newPlugins, { shouldDirty: true });
    },
    [setValue, plugins]
  );

  const handlePluginEdit = useCallback(
    (index: number) => {
      setSelectedForEditPluginIndex(index);
      onOpen();
    },
    [onOpen]
  );

  const handlePluginRemove = useCallback(
    (index) => {
      const updatedPlugins = plugins.filter((_, idx) => idx !== index);
      setValue("plugins", updatedPlugins, { shouldDirty: true });
    },
    [setValue, plugins]
  );

  const handlePluginSave = useCallback(async () => {
    if (textareaRef.current) {
      const newPlugins = [...plugins];
      newPlugins[selectedForEditPluginIndex!].url = textareaRef.current.value;

      const plugin: PluginEntry = await post(API_ROUTES.GET_PLUGIN_CONFIG, {
        arg: { plugin: newPlugins[selectedForEditPluginIndex!] },
      });
      // disable all existing plugins and enable new one
      newPlugins.forEach((plugin) => (plugin.enabled = false));
      newPlugins[selectedForEditPluginIndex!].enabled = true;
      newPlugins[selectedForEditPluginIndex!].plugin_config = plugin.plugin_config;
      setValue("plugins", newPlugins, { shouldDirty: true });
    }
    onClose();
  }, [onClose, control, plugins, selectedForEditPluginIndex]);

  const handlePluginAdd = useCallback(() => {
    const newPlugin: PluginEntry = {
      url: "",
      enabled: false,
    };
    setValue("plugins", [...plugins, newPlugin]);
    handlePluginEdit(plugins.length);
  }, [setValue, plugins, handlePluginEdit]);

  return (
    <FormControl ref={containerRef}>
      <Menu placement="auto">
        <MenuButton as={Button} pr="3" rightIcon={<Cog />} size="lg" width="100%">
          {activePluginIndex > -1 && plugins[activePluginIndex]?.enabled ? (
            <Box display="flex" justifyContent="flex-start" gap={2}>
              <Image
                src={plugins[activePluginIndex]?.plugin_config?.logo_url}
                alt="Plugins"
                width="25px"
                height="25px"
                marginRight="5px"
              />
              <Text mt="4px" fontSize="sm" isTruncated>
                {plugins[activePluginIndex]?.plugin_config?.name_for_human}
              </Text>
            </Box>
          ) : (
            <Box display="flex" justifyContent="center" gap={2}>
              <AttachmentIcon boxSize="5" />
              {t("plugins")}
            </Box>
          )}
        </MenuButton>
        <Box position="fixed" zIndex="1">
          <MenuList left="-150px" position="absolute" w="280px">
            <RadioGroup value={plugins?.findIndex((plugin) => plugin.enabled).toString()}>
              {plugins?.map((plugin, index) => (
                <MenuItem key={index}>
                  <Radio value={index.toString()} onClick={() => handlePluginSelect(index)}>
                    <Box
                      display="flex"
                      justifyContent="flex-start"
                      gap={2}
                      mr="4"
                      onClick={() => handlePluginSelect(index)}
                    >
                      <Image
                        src={plugins[index]?.plugin_config?.logo_url}
                        alt="Plugins"
                        width="25px"
                        height="25px"
                        marginRight="5px"
                      />
                      <Box position="absolute" top="-2px" left="33px">
                        {!plugins[index]?.trusted ? (
                          <Tooltip label={t("unverified_plugin_description")}>
                            <Box
                              display="flex"
                              alignItems="center"
                              marginLeft="2"
                              bg="red.100"
                              borderRadius="100%"
                              p="0"
                            >
                              <WarningIcon boxSize="3" color="red.600" />
                            </Box>
                          </Tooltip>
                        ) : (
                          <Tooltip label={t("verified_plugin_description")}>
                            <Box
                              display="flex"
                              alignItems="center"
                              marginLeft="2"
                              bg="gray.100"
                              borderRadius="100%"
                              p="0"
                            >
                              <CheckCircleIcon boxSize="3" color="green.400" />
                            </Box>
                          </Tooltip>
                        )}
                      </Box>
                      <Tooltip label={plugins[index]?.plugin_config?.description_for_human}>
                        <Text fontSize="sm">{plugins[index]?.plugin_config?.name_for_human}</Text>
                      </Tooltip>
                    </Box>
                  </Radio>
                  <IconButton
                    aria-label={t("edit_plugin")}
                    icon={<Edit />}
                    onClick={() => handlePluginEdit(index)}
                    size="sm"
                    marginLeft="auto"
                  />
                  <IconButton
                    aria-label={t("remove_plugin")}
                    icon={<CloseIcon />}
                    onClick={() => handlePluginRemove(index)}
                    size="sm"
                    marginLeft="2"
                  />
                </MenuItem>
              ))}
            </RadioGroup>
            <MenuItem onClick={handlePluginAdd}>
              <Box w="100%" display="flex" justifyContent="center">
                <IconButton aria-label={t("add_plugin")} icon={<Plus />} size="sm" />
              </Box>
            </MenuItem>
          </MenuList>
        </Box>
      </Menu>
      <Modal isOpen={isOpen} onClose={onClose} size="xl">
        <ModalOverlay />
        <ModalContent>
          <ModalHeader>{t("edit_plugin")}</ModalHeader>
          <ModalCloseButton />
          <ModalBody>
            <Textarea
              minHeight="40px"
              defaultValue={selectedForEditPluginIndex !== null ? plugins[selectedForEditPluginIndex!]?.url : ""}
              ref={textareaRef}
              mb={4}
            />
            <Box as="pre" whiteSpace="pre-wrap" fontSize="xs">
              {JSON.stringify(plugins[selectedForEditPluginIndex!], null, 4)}
            </Box>
          </ModalBody>
          <ModalFooter>
            <Button colorScheme="blue" onClick={handlePluginSave}>
              {t("save")}
            </Button>
          </ModalFooter>
        </ModalContent>
      </Modal>
    </FormControl>
  );
};
