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
// i need
import { AttachmentIcon, WarningIcon, CheckCircleIcon, CloseIcon } from "@chakra-ui/icons";
import { ChangeEvent, useCallback, useEffect, useState, useRef } from "react";
import { useTranslation } from "next-i18next";
import { Controller, useFormContext, useWatch } from "react-hook-form";
import { ChatConfigFormData } from "src/types/Chat";
import { useChatContext } from "./ChatContext";
import { PluginEntry } from "src/types/Chat";
import { get, post } from "src/lib/api";
import { API_ROUTES } from "src/lib/routes";

export const PluginsChooser = () => {
  const { t } = useTranslation("common");
  const { control, register, reset, setValue } = useFormContext<ChatConfigFormData>();
  const [selectedPluginIndex, setSelectedPluginIndex] = useState<number | null>(null);
  const { isOpen, onOpen, onClose } = useDisclosure();

  const textareaRef = useRef<HTMLTextAreaElement | null>(null);
  const plugins = useWatch({ name: "plugins", control: control });

  const findSelectedPluginIndex = useCallback(() => {
    return plugins.findIndex((plugin) => plugin.enabled);
  }, [plugins]);

  const handlePluginSelect = useCallback(
    (index: number) => {
      const selectedIndex = plugins.findIndex((plugin) => plugin.enabled);
      const newPlugins = plugins.map((plugin, i) => ({
        ...plugin,
        enabled: selectedIndex === index ? false : i === index,
      }));
      setValue("plugins", newPlugins);
    },
    [setValue, plugins]
  );

  const handlePluginEdit = useCallback(
    (index: number) => {
      setSelectedPluginIndex(index);
      onOpen();
    },
    [onOpen]
  );

  const handlePluginRemove = useCallback(
    (index) => {
      const updatedPlugins = plugins.filter((_, idx) => idx !== index);
      setValue("plugins", updatedPlugins);
    },
    [setValue, plugins]
  );

  const handlePluginSave = useCallback(async () => {
    if (textareaRef.current) {
      const newPlugins = [...plugins];
      newPlugins[selectedPluginIndex!].url = textareaRef.current.value;

      const plugin: PluginEntry = await post(API_ROUTES.GET_PLUGIN_CONFIG, {
        arg: { plugin: newPlugins[selectedPluginIndex!] },
      });

      newPlugins[selectedPluginIndex!].plugin_config = plugin.plugin_config;
      setValue("plugins", newPlugins);
    }
    onClose();
  }, [onClose, control, plugins, selectedPluginIndex]);

  const handlePluginAdd = useCallback(() => {
    const newPlugin: PluginEntry = {
      url: "",
      enabled: false,
    };
    setValue("plugins", [...plugins, newPlugin]);
    handlePluginEdit(plugins.length);
  }, [setValue, plugins, handlePluginEdit]);

  const limitPluginNameLength = (name: string) => {
    if (!name) {
      return "";
    }
    if (name.length > 15) {
      return name.substring(0, 15) + "...";
    }
    return name;
  };

  return (
    <FormControl>
      <Menu>
        <MenuButton as={Button} rightIcon={<Cog />} w="100%" size="lg">
          {plugins && plugins[findSelectedPluginIndex()]?.enabled ? (
            <Box display="flex" justifyContent="center" gap={2}>
              <Image
                src={plugins[findSelectedPluginIndex()]?.plugin_config?.logo_url}
                alt="Plugins"
                width="25px"
                height="25px"
                marginRight="5px"
              />
              <Text>{limitPluginNameLength(plugins[findSelectedPluginIndex()]?.plugin_config?.name_for_human)}</Text>
            </Box>
          ) : (
            <Box display="flex" justifyContent="center" gap={2}>
              <AttachmentIcon boxSize="5" />
              {t("plugins")}
            </Box>
          )}
        </MenuButton>
        <MenuList>
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
                    {plugins[index]?.plugin_config?.name_for_human}
                    {!plugins[index]?.trusted ? (
                      <Tooltip label={t("unverified_plugin_description")}>
                        <Box display="flex" alignItems="center" marginLeft="2">
                          <WarningIcon boxSize="4" color="red.600" />
                        </Box>
                      </Tooltip>
                    ) : (
                      <Tooltip label={t("verified_plugin_description")}>
                        <Box display="flex" alignItems="center" marginLeft="2">
                          <CheckCircleIcon boxSize="4" color="green.400" />
                        </Box>
                      </Tooltip>
                    )}
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
      </Menu>
      <Modal isOpen={isOpen} onClose={onClose} size="xl">
        <ModalOverlay />
        <ModalContent>
          <ModalHeader>{t("edit_plugin")}</ModalHeader>
          <ModalCloseButton />
          <ModalBody>
            <Textarea
              minHeight="480px"
              defaultValue={selectedPluginIndex !== null ? plugins[selectedPluginIndex!].url : ""}
              ref={textareaRef}
            />
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
