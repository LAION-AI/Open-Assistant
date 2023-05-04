import { AttachmentIcon, CheckCircleIcon, CloseIcon, WarningIcon } from "@chakra-ui/icons";
import {
  Box,
  Button,
  FormControl,
  IconButton,
  Image,
  Input,
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
  Radio,
  RadioGroup,
  Text,
  Tooltip,
  useDisclosure,
} from "@chakra-ui/react";
import { Cog, Edit, Plus } from "lucide-react";
import { useTranslation } from "next-i18next";
import { useCallback, useMemo, useRef, useState } from "react";
import { useFormContext } from "react-hook-form";
import { post } from "src/lib/api";
import { API_ROUTES } from "src/lib/routes";
import { ChatConfigFormData } from "src/types/Chat";
import { PluginEntry } from "src/types/Chat";

export type PluginsChooserProps = {
  plugins: PluginEntry[];
  onAddPlugin: (plugin: PluginEntry) => void;
};

export const PluginsChooser = ({ plugins, onAddPlugin }: PluginsChooserProps) => {
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
    const url = textareaRef.current?.value.trim();
    if (!url) {
      onClose();
      return;
    }

    const isPluginExists = plugins.some((plugin) => plugin.url === url);

    if (isPluginExists) {
      onClose();
      return;
    }

    const plugin: PluginEntry = await post(API_ROUTES.GET_PLUGIN_CONFIG, {
      arg: {
        plugin: {
          url,
          enable: true,
        },
      },
    });

    onAddPlugin(plugin);

    onClose();
  }, [plugins, onClose, onAddPlugin]);

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
                <MenuItem key={index} as="div">
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
            <MenuItem onClick={onOpen}>
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
            <Input
              type="url"
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
