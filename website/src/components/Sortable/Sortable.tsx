import { Flex } from "@chakra-ui/react";
import {
  closestCenter,
  DndContext,
  KeyboardSensor,
  MouseSensor,
  TouchSensor,
  useSensor,
  useSensors,
} from "@dnd-kit/core";
import type { DragEndEvent } from "@dnd-kit/core/dist/types/events";
import { restrictToParentElement, restrictToVerticalAxis } from "@dnd-kit/modifiers";
import {
  arrayMove,
  SortableContext,
  sortableKeyboardCoordinates,
  verticalListSortingStrategy,
} from "@dnd-kit/sortable";
import { ReactNode, useEffect, useState } from "react";

import { CollapsableText } from "../CollapsableText";
import { SortableItem } from "./SortableItem";

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
    useSensor(MouseSensor, { activationConstraint: { distance: 4 } }),
    useSensor(TouchSensor, { activationConstraint: { distance: 4 } }),
    useSensor(KeyboardSensor, { coordinateGetter: sortableKeyboardCoordinates })
  );

  const extraClasses = props.className || "";

  return (
    <DndContext
      sensors={sensors}
      collisionDetection={closestCenter}
      onDragEnd={handleDragEnd}
      modifiers={[restrictToParentElement, restrictToVerticalAxis]}
    >
      <SortableContext items={itemsWithIds} strategy={verticalListSortingStrategy}>
        <Flex direction="column" gap={2} className={extraClasses}>
          {itemsWithIds.map(({ id, item }, index) => (
            <SortableItem key={id} id={id} index={index} isEditable={props.isEditable} isDisabled={props.isDisabled}>
              <CollapsableText text={item} isDisabled={props.isDisabled} />
            </SortableItem>
          ))}
        </Flex>
      </SortableContext>
    </DndContext>
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
