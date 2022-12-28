import { ArrowUpIcon, ArrowDownIcon } from "@heroicons/react/20/solid";
import { Button } from "src/components/Button";
import clsx from "clsx";

export interface SortableItemProps {
  canIncrement: boolean;
  canDecrement: boolean;
  onIncrement: () => void;
  onDecrement: () => void;
  children: React.ReactNode;
}

export const SortableItem = ({ canIncrement, canDecrement, onIncrement, onDecrement, children }: SortableItemProps) => {
  return (
    <li className="grid grid-cols-[min-content_1fr] items-center rounded-lg shadow-md gap-x-2 p-2">
      <ArrowButton active={canIncrement} onClick={onIncrement}>
        <ArrowUpIcon width={28} />
      </ArrowButton>
      <span style={{ gridRow: "span 2" }}>{children}</span>

      <ArrowButton active={canDecrement} onClick={onDecrement}>
        <ArrowDownIcon width={28} />
      </ArrowButton>
    </li>
  );
};

interface ArrowButtonProps {
  active: boolean;
  onClick: () => void;
  children: React.ReactNode;
}

const ArrowButton = ({ children, active, onClick }: ArrowButtonProps) => {
  return (
    <Button
      className={clsx("justify-center", active ? "hover:bg-indigo-200" : "opacity-10")}
      onClick={onClick}
      disabled={!active}
    >
      {children}
    </Button>
  );
};
