import {
  Box,
  Checkbox,
  Flex,
  Modal,
  ModalBody,
  ModalCloseButton,
  ModalContent,
  ModalHeader,
  ModalOverlay,
  Slider,
  SliderFilledTrack,
  SliderThumb,
  SliderTrack,
  Switch,
  Text,
  useDisclosure,
} from "@chakra-ui/react";
import {
  closestCenter,
  DndContext,
  KeyboardSensor,
  MouseSensor,
  PointerSensor,
  useSensor,
  useSensors,
} from "@dnd-kit/core";
import type { DragEndEvent } from "@dnd-kit/core/dist/types/events";
import { restrictToVerticalAxis, restrictToWindowEdges } from "@dnd-kit/modifiers";
import {
  arrayMove,
  SortableContext,
  sortableKeyboardCoordinates,
  verticalListSortingStrategy,
} from "@dnd-kit/sortable";
import { lazy, Suspense, useCallback, useEffect, useState } from "react";
import { useTranslation } from "next-i18next";
import { Message } from "src/types/Conversation";

import { CollapsableText } from "../CollapsableText";
import { SortableItem } from "./SortableItem";

const RenderedMarkdown = lazy(() => import("../Messages/RenderedMarkdown"));

export interface SortableProps {
  items: Message[];
  onChange?: (newSortedIndices: number[]) => void;
  isEditable: boolean;
  isDisabled?: boolean;
  className?: string;
  revealSynthetic?: boolean;
}

interface SortableItemType {
  id: number;
  originalIndex: number;
  item: Message;
}

// Local storage keys
const STORAGE_KEYS = {
  horizontalLayout: "oa-sortable-horizontal-layout",
  removeContentLimit: "oa-sortable-remove-content-limit",
  messagesPerRow: "oa-sortable-messages-per-row",
};

export const Sortable = ({ onChange, revealSynthetic, ...props }: SortableProps) => {
  const [itemsWithIds, setItemsWithIds] = useState<SortableItemType[]>([]);
  const [modalText, setModalText] = useState<string | null>(null);
  
  // UI preferences from local storage
  const [isHorizontal, setIsHorizontal] = useState<boolean>(() => {
    if (typeof window !== "undefined") {
      return localStorage.getItem(STORAGE_KEYS.horizontalLayout) === "true";
    }
    return false;
  });
  
  const [removeContentLimit, setRemoveContentLimit] = useState<boolean>(() => {
    if (typeof window !== "undefined") {
      return localStorage.getItem(STORAGE_KEYS.removeContentLimit) === "true";
    }
    return false;
  });
  
  const [messagesPerRow, setMessagesPerRow] = useState<number>(() => {
    if (typeof window !== "undefined") {
      const saved = localStorage.getItem(STORAGE_KEYS.messagesPerRow);
      return saved ? parseInt(saved, 10) : 3;
    }
    return 3;
  });

  const { t } = useTranslation("tasks");
  useEffect(() => {
    setItemsWithIds(
      props.items.map((item, idx) => ({
        item,
        id: idx + 1, // +1 because dndtoolkit has problem with "falsy" ids
        originalIndex: idx,
      }))
    );
  }, [props.items]);

  // Save preferences to local storage
  useEffect(() => {
    if (typeof window !== "undefined") {
      localStorage.setItem(STORAGE_KEYS.horizontalLayout, String(isHorizontal));
    }
  }, [isHorizontal]);

  useEffect(() => {
    if (typeof window !== "undefined") {
      localStorage.setItem(STORAGE_KEYS.removeContentLimit, String(removeContentLimit));
    }
  }, [removeContentLimit]);

  useEffect(() => {
    if (typeof window !== "undefined") {
      localStorage.setItem(STORAGE_KEYS.messagesPerRow, String(messagesPerRow));
    }
  }, [messagesPerRow]);

  const sensors = useSensors(
    useSensor(PointerSensor, {
      activationConstraint: { distance: 8, tolerance: 100 },
    }),
    useSensor(MouseSensor, { activationConstraint: { distance: 10 } }),
    useSensor(KeyboardSensor, {
      coordinateGetter: sortableKeyboardCoordinates,
    })
  );
  const { isOpen, onOpen, onClose } = useDisclosure();
  const extraClasses = props.className || "";

  const handleDragEnd = useCallback(
    (event: DragEndEvent) => {
      const { active, over } = event;
      if (active.id === over?.id) {
        return;
      }
      setItemsWithIds((items) => {
        const oldIndex = items.findIndex((x) => x.id === active.id);
        const newIndex = items.findIndex((x) => x.id === over?.id);
        const newArray = arrayMove(items, oldIndex, newIndex);
        onChange && onChange(newArray.map((item) => item.originalIndex));
        return newArray;
      });
    },
    [onChange]
  );

  // Handle horizontal layout toggle
  const handleLayoutToggle = useCallback(() => {
    setIsHorizontal((prev) => !prev);
  }, []);

  // Handle content limit toggle
  const handleContentLimitToggle = useCallback(() => {
    setRemoveContentLimit((prev) => !prev);
  }, []);

  // Handle messages per row change
  const handleMessagesPerRowChange = useCallback((value: number) => {
    setMessagesPerRow(value);
  }, []);

  // Calculate flex wrap style for horizontal layout
  const containerStyle = isHorizontal
    ? { flexWrap: "wrap" as const, gap: "16px" }
    : { flexDirection: "column" as const, gap: "16px" };

  const itemWidth = isHorizontal ? `${100 / messagesPerRow - 2}%` : "100%";

  return (
    <>
      {/* Control Panel */}
      <Box mb={4} p={4} borderWidth="1px" borderRadius="lg" bg="gray.50" _dark={{ bg: "gray.700" }}>
        <Flex direction={{ base: "column", md: "row" }} gap={4} align="center" wrap="wrap">
          {/* Layout Toggle */}
          <Flex align="center" gap={2}>
            <Switch
              id="layout-toggle"
              isChecked={isHorizontal}
              onChange={handleLayoutToggle}
            />
            <Text fontSize="sm">
              {isHorizontal ? t("horizontal_layout") : t("vertical_layout")}
            </Text>
          </Flex>

          {/* Content Limit Toggle */}
          <Flex align="center" gap={2}>
            <Checkbox
              id="content-limit-toggle"
              isChecked={removeContentLimit}
              onChange={handleContentLimitToggle}
            />
            <Text fontSize="sm">{t("show_full_content")}</Text>
          </Flex>

          {/* Messages Per Row Slider (only in horizontal mode) */}
          {isHorizontal && (
            <Flex align="center" gap={3} flex={1} minW="200px">
              <Text fontSize="sm" whiteSpace="nowrap">
                {t("messages_per_row")}: {messagesPerRow}
              </Text>
              <Slider
                value={messagesPerRow}
                onChange={handleMessagesPerRowChange}
                min={1}
                max={Math.max(1, itemsWithIds.length)}
                step={1}
                flex={1}
              >
                <SliderTrack>
                  <SliderFilledTrack />
                </SliderTrack>
                <SliderThumb />
              </Slider>
            </Flex>
          )}
        </Flex>
      </Box>

      <DndContext
        sensors={sensors}
        collisionDetection={closestCenter}
        onDragEnd={handleDragEnd}
        modifiers={[restrictToWindowEdges, restrictToVerticalAxis]}
      >
        <SortableContext items={itemsWithIds} strategy={verticalListSortingStrategy}>
          <Flex {...containerStyle} className={extraClasses}>
            {itemsWithIds.map(({ id, item }, index) => (
              <Box key={id} width={itemWidth} minW={isHorizontal ? "250px" : "100%"}>
                <SortableItem
                  OpenModal={() => {
                    setModalText(item.text);
                    onOpen();
                  }}
                  id={id}
                  index={index}
                  isEditable={props.isEditable}
                  isDisabled={!!props.isDisabled}
                  synthetic={item.synthetic && !!revealSynthetic}
                >
                  <button
                    className="w-full text-left"
                    aria-label="show full text"
                    onClick={() => {
                      setModalText(item.text);
                      onOpen();
                    }}
                  >
                    <CollapsableText text={item.text} isCollapsed={!removeContentLimit} />
                  </button>
                </SortableItem>
              </Box>
            ))}
          </Flex>
        </SortableContext>
      </DndContext>
      <Modal
        isOpen={isOpen}
        onClose={() => {
          setModalText(null);
          onClose();
        }}
        size="6xl"
        scrollBehavior={"inside"}
        isCentered
      >
        <ModalOverlay>
          <ModalContent pb={5} alignItems="center">
            <ModalHeader>{t("full_text")}</ModalHeader>
            <ModalCloseButton />
            <ModalBody maxW="full">
              <Suspense fallback={modalText}>
                <RenderedMarkdown markdown={modalText || ""}></RenderedMarkdown>
              </Suspense>
            </ModalBody>
          </ModalContent>
        </ModalOverlay>
      </Modal>
    </>
  );
};
