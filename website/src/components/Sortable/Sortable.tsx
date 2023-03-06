import {
  Flex,
  Modal,
  ModalBody,
  ModalCloseButton,
  ModalContent,
  ModalHeader,
  ModalOverlay,
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

interface SortableItem {
  id: number;
  originalIndex: number;
  item: Message;
}

export const Sortable = ({ onChange, revealSynthetic, ...props }: SortableProps) => {
  const [itemsWithIds, setItemsWithIds] = useState<SortableItem[]>([]);
  const [modalText, setModalText] = useState<string | null>(null);
  useEffect(() => {
    setItemsWithIds(
      props.items.map((item, idx) => ({
        item,
        id: idx + 1, // +1 because dndtoolkit has problem with "falsy" ids
        originalIndex: idx,
      }))
    );
  }, [props.items]);

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

  return (
    <>
      <DndContext
        sensors={sensors}
        collisionDetection={closestCenter}
        onDragEnd={handleDragEnd}
        modifiers={[restrictToWindowEdges, restrictToVerticalAxis]}
      >
        <SortableContext items={itemsWithIds} strategy={verticalListSortingStrategy}>
          <Flex direction="column" gap={4} className={extraClasses}>
            {itemsWithIds.map(({ id, item }, index) => (
              <SortableItem
                OpenModal={() => {
                  setModalText(item.text);
                  onOpen();
                }}
                key={id}
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
                  <CollapsableText text={item.text} />
                </button>
              </SortableItem>
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
            <ModalHeader>Full Text</ModalHeader>
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
