import { AttachmentIcon } from "@chakra-ui/icons";
import {
  Avatar,
  Box,
  Button,
  FormControl,
  FormLabel,
  IconButton,
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
  Text,
  Tooltip,
  useBoolean,
  useDisclosure,
  useToast,
} from "@chakra-ui/react";
import { AlertCircle, CheckCircle2, Edit, Eye, Plus } from "lucide-react";
import { X } from "lucide-react";
import { useTranslation } from "next-i18next";
import { useCallback, useRef, useState } from "react";
import { MouseEvent } from "react";
import { useFormContext } from "react-hook-form";
import SimpleBar from "simplebar-react";
import { post } from "src/lib/api";
import { OasstError } from "src/lib/oasst_api_client";
import { API_ROUTES } from "src/lib/routes";
import { ChatConfigFormData, PluginEntry } from "src/types/Chat";

import { JsonCard } from "../JsonCard";
import { useChatPluginContext } from "./ChatPluginContext";

export type PluginsChooserProps = {
  plugins: PluginEntry[];
};

export const PluginsChooser = () => {
  const { t } = useTranslation("chat");
  const { t: tCommon } = useTranslation();
  const { setValue, getValues } = useFormContext<ChatConfigFormData>();
  const { plugins, setPlugins } = useChatPluginContext();
  const [selectedForEditPluginIndex, setSelectedForEditPluginIndex] = useState<number | null>(null);
  const { isOpen, onOpen, onClose } = useDisclosure();

  const textareaRef = useRef<HTMLInputElement | null>(null);

  const handlePluginSelect = useCallback(
    (index: number) => {
      const plugin = plugins[index];
      if (plugin) {
        setValue("plugins", [plugin], { shouldDirty: true });
      }
    },
    [plugins, setValue]
  );

  const handlePluginEdit = useCallback(
    (index: number) => {
      setSelectedForEditPluginIndex(index);
      onOpen();
      console.log(plugins[index]);
    },
    [onOpen, plugins]
  );

  const isCreatePlugin = selectedForEditPluginIndex === null;

  const handlePluginDelete = useCallback(
    (index: number) => {
      const selectedPlugin = getValues("plugins")[0];

      if (selectedPlugin?.url === plugins[index].url) {
        setValue("plugins", [], { shouldDirty: true });
      }

      setPlugins((prev) => prev.filter((_, i) => i !== index));
    },
    [getValues, plugins, setPlugins, setValue]
  );

  const [loading, setLoading] = useBoolean();
  const toast = useToast();
  const handlePluginSave = useCallback(async () => {
    const url = textareaRef.current?.value.trim();
    if (!url) {
      onClose();
      return;
    }

    const isPluginExists = plugins.some((plugin) => plugin.url === url);

    setLoading.on();
    try {
      const newPlugin: PluginEntry = await post(API_ROUTES.GET_PLUGIN_CONFIG, {
        arg: {
          plugin: {
            url,
            enable: true,
          },
        },
      });
      if (isCreatePlugin) {
        if (isPluginExists) {
          toast({
            title: "Plugin already exists",
          });
        } else {
          setPlugins((prev) => [...prev, newPlugin]);
          setValue("plugins", [newPlugin], { shouldDirty: true });
        }
      } else {
        const editingPlugin = plugins[selectedForEditPluginIndex!];
        if (editingPlugin.url === getValues("plugins")[0]?.url) {
          setValue("plugins", [newPlugin], { shouldDirty: true });
        }
        setPlugins((prev) => {
          prev[selectedForEditPluginIndex!] = newPlugin;
          return prev;
        });
      }
    } catch (e) {
      if (e instanceof OasstError) {
        toast({
          title: "Unable to load",
          status: "error",
        });
      }
    }

    setLoading.off();
    onClose();
  }, [
    plugins,
    setLoading,
    onClose,
    isCreatePlugin,
    setPlugins,
    selectedForEditPluginIndex,
    getValues,
    setValue,
    toast,
  ]);

  const selectedPlugin = getValues("plugins")?.[0];

  return (
    <FormControl>
      <FormLabel>{t("plugins")}</FormLabel>
      <Menu placement="auto" isLazy lazyBehavior="keepMounted">
        <MenuButton as={Button} width="100%" size="lg">
          {selectedPlugin ? (
            <Box display="flex" gap={2}>
              <PluginImage plugin={selectedPlugin}></PluginImage>
              <Text mt="4px" fontSize="sm" isTruncated>
                {selectedPlugin.plugin_config?.name_for_human}
              </Text>
            </Box>
          ) : (
            <Box display="flex" justifyContent="center" gap={2}>
              <AttachmentIcon boxSize="5" />
              {t("plugins")}
            </Box>
          )}
        </MenuButton>
        <MenuList w="235px" pb="0" mr="100px">
          <SimpleBar
            style={{ maxHeight: "250px" }}
            classNames={{
              contentEl: "space-y-2 flex flex-col overflow-y-auto",
            }}
          >
            {plugins?.map((plugin, index) => (
              <PluginOption
                key={index}
                index={index}
                plugin={plugin}
                onChange={handlePluginSelect}
                onEdit={handlePluginEdit}
                onDelete={handlePluginDelete}
              ></PluginOption>
            ))}
          </SimpleBar>

          <MenuItem
            bg="gray.100"
            _hover={{ bg: "gray.200" }}
            onClick={() => {
              setSelectedForEditPluginIndex(null);
              onOpen();
            }}
          >
            <Box w="100%" display="flex" justifyContent="center">
              <IconButton aria-label={t("add_plugin")} icon={<Plus />} size="sm" bg="transparent" />
            </Box>
          </MenuItem>
        </MenuList>
      </Menu>
      <Modal isOpen={isOpen} onClose={onClose} size="xl">
        <ModalOverlay />
        <ModalContent>
          <ModalHeader>{isCreatePlugin ? t("add_plugin") : t("edit_plugin")}</ModalHeader>
          <ModalCloseButton />
          <ModalBody>
            <Input type="url" defaultValue={plugins[selectedForEditPluginIndex!]?.url} ref={textareaRef} mb={4} />
            {selectedForEditPluginIndex !== null && <JsonCard>{plugins[selectedForEditPluginIndex]}</JsonCard>}
          </ModalBody>
          <ModalFooter>
            <Button colorScheme="blue" onClick={handlePluginSave} isLoading={loading}>
              {tCommon("save")}
            </Button>
          </ModalFooter>
        </ModalContent>
      </Modal>
    </FormControl>
  );
};

const PluginOption = ({
  index,
  plugin,
  onChange: onChange,
  onDelete,
  onEdit,
}: {
  index: number;
  plugin: PluginEntry;
  onChange: (index: number) => void;
  onEdit: (index: number) => void;
  onDelete: (index: number) => void;
}) => {
  const { t } = useTranslation("chat");

  const handleClick = useCallback(() => {
    onChange(index);
  }, [index, onChange]);

  const handleEdit = useCallback(
    (e: MouseEvent) => {
      e.stopPropagation();
      onEdit(index);
    },
    [index, onEdit]
  );

  const handleDelete = useCallback(
    (e: MouseEvent) => {
      e.stopPropagation();
      onDelete(index);
    },
    [index, onDelete]
  );

  const { trusted, plugin_config } = plugin;
  const editIcon = trusted ? <Eye size="12px" /> : <Edit size="12px" />;
  return (
    <MenuItem
      display="flex"
      alignItems="center"
      py="2"
      px="4"
      gap={2}
      _hover={{
        bg: "gray.200",
      }}
      _dark={{
        _hover: {
          bg: "gray.600",
        },
      }}
      onClick={handleClick}
    >
      <Tooltip label={plugin_config?.description_for_human} placement="left">
        <Box display="flex" gap={2} w="full" alignItems="center">
          <Box position="relative">
            <PluginImage plugin={plugin}></PluginImage>
            <Box position="absolute" top="-4px" right="-4px" bg={trusted ? "green.100" : "red.100"} borderRadius="full">
              <Tooltip
                label={trusted ? t("verified_plugin_description") : t("unverified_plugin_description")}
                placement="left"
              >
                <Box as={trusted ? CheckCircle2 : AlertCircle} size="12px" color={trusted ? "green.400" : "red.600"} />
              </Tooltip>
            </Box>
          </Box>
          <Text fontSize="sm">{plugin_config?.name_for_human}</Text>
        </Box>
      </Tooltip>
      <IconButton
        aria-label={t(trusted ? "view_plugin" : "edit_plugin")}
        icon={editIcon}
        onClick={handleEdit}
        size="xs"
      />
      {!trusted && (
        <IconButton aria-label={t("remove_plugin")} icon={<X size="12px" />} onClick={handleDelete} size="xs" />
      )}
    </MenuItem>
  );
};

const PluginImage = ({ plugin }: { plugin: PluginEntry }) => {
  return (
    <Avatar
      src={plugin.plugin_config?.logo_url || ""}
      width="25px"
      height="25px"
      borderRadius="sm"
      name={plugin.plugin_config?.name_for_human}
    />
  );
};
