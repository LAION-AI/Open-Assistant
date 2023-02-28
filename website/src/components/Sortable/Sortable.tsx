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
import { lazy, ReactNode, Suspense, useEffect, useState } from "react";

import { CollapsableText } from "../CollapsableText";
import { SortableItem } from "./SortableItem";

const RenderedMarkdown = lazy(() => import("../Messages/RenderedMarkdown"));

export interface SortableProps {
  items: ReactNode[];
  onChange?: (newSortedIndices: number[]) => void;
  isEditable: boolean;
  isDisabled?: boolean;
  className?: string;
}

interface SortableItems {
  id: number;
  originalIndex: number;
  item: ReactNode;
}

export const Sortable = (props: SortableProps) => {
  const [itemsWithIds, setItemsWithIds] = useState<SortableItems[]>([]);
  const [modalText, setModalText] = useState(null);
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

  return (
    <>
      <DndContext
        sensors={sensors}
        collisionDetection={closestCenter}
        onDragEnd={handleDragEnd}
        modifiers={[restrictToWindowEdges, restrictToVerticalAxis]}
      >
        <SortableContext items={itemsWithIds} strategy={verticalListSortingStrategy}>
          <Flex direction="column" gap={2} className={extraClasses}>
            {itemsWithIds.map(({ id, item }, index) => (
              <SortableItem
                OpenModal={() => {
                  setModalText(item);
                  onOpen();
                }}
                key={id}
                id={id}
                index={index}
                isEditable={props.isEditable}
                isDisabled={props.isDisabled}
              >
                <button
                  className="w-full text-left"
                  aria-label="show full text"
                  onClick={() => {
                    setModalText(item);
                    onOpen();
                  }}
                >
                  <CollapsableText text={item} />
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
                <RenderedMarkdown markdown={modalText}></RenderedMarkdown>
              </Suspense>
            </ModalBody>
          </ModalContent>
        </ModalOverlay>
      </Modal>
    </>
  );

  function handleDragEnd(event: DragEndEvent) {
    const { active, over } = event;
    if (active.id === over.id) {
      return;
    }
    setItemsWithIds((items) => {
      const oldIndex = items.findIndex((x) => x.id === active.id);
      const newIndex = items.findIndex((x) => x.id === over.id);
      const newArray = arrayMove(items, oldIndex, newIndex);
      props.onChange && props.onChange(newArray.map((item) => item.originalIndex));
      return newArray;
    });
  }
};
