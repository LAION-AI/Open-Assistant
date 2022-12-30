import { ReactNode, useEffect, useState } from "react";
import { SortableItem } from "./SortableItem";

export interface SortableProps {
  items: ReactNode[];
  onChange: (newSortedIndices: number[]) => void;
}

export const Sortable = ({ items, onChange }) => {
  const [sortOrder, setSortOrder] = useState<number[]>([]);

  const update = (newRanking: number[]) => {
    setSortOrder(newRanking);
    onChange(newRanking);
  };

  useEffect(() => {
    const indices = Array.from({ length: items.length }).map((_, i) => i);
    setSortOrder(indices);
    onChange(indices);
  }, [items, onChange]);

  return (
    <ul className="flex flex-col gap-4">
      {sortOrder.map((rank, i) => (
        <SortableItem
          key={`${rank}`}
          canIncrement={i > 0}
          onIncrement={() => {
            const newRanking = sortOrder.slice();
            const newIdx = i - 1;
            [newRanking[i], newRanking[newIdx]] = [newRanking[newIdx], newRanking[i]];
            update(newRanking);
          }}
          canDecrement={i < sortOrder.length - 1}
          onDecrement={() => {
            const newRanking = sortOrder.slice();
            const newIdx = i + 1;
            [newRanking[i], newRanking[newIdx]] = [newRanking[newIdx], newRanking[i]];
            update(newRanking);
          }}
        >
          {items[rank]}
        </SortableItem>
      ))}
    </ul>
  );
};
