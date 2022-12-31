import { Flex } from "@chakra-ui/react";
import { closestCenter, DndContext, PointerSensor, TouchSensor, useSensor, useSensors } from "@dnd-kit/core";
import type { DragEndEvent } from "@dnd-kit/core/dist/types/events";
import { arrayMove, SortableContext, verticalListSortingStrategy } from "@dnd-kit/sortable";
import { ReactNode, useEffect, useState } from "react";

import { SortableItem } from "./SortableItem";

export interface SortableProps {
  items: ReactNode[];
  onChange: (newSortedIndices: number[]) => void;
}

interface SortableItems {
  id: number;
  originalIndex: number;
  item: ReactNode;
}

export const Sortable = ({ items, onChange }: SortableProps) => {
  const [itemsWithIds, setItemsWithIds] = useState<SortableItems[]>([]);

  useEffect(() => {
    setItemsWithIds(
      items.map((item, idx) => ({
        item,
        id: idx + 1, // +1 because dndtoolkit has problem with "falsy" ids
        originalIndex: idx,
      }))
    );
  }, [items]);

  const sensors = useSensors(useSensor(PointerSensor), useSensor(TouchSensor));

  return (
    <DndContext sensors={sensors} collisionDetection={closestCenter} onDragEnd={handleDragEnd}>
      <SortableContext items={itemsWithIds} strategy={verticalListSortingStrategy}>
        <Flex direction="column" gap={2}>
          {itemsWithIds.map(({ id, item }) => (
            <SortableItem key={id} id={id}>
              {item}
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
      onChange(newArray.map((item) => item.originalIndex));
      return newArray;
    });
  }
};
