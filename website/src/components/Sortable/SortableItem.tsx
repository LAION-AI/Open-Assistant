import { Button } from "@chakra-ui/react";
import { useColorMode } from "@chakra-ui/react";
import { useSortable } from "@dnd-kit/sortable";
import { CSS } from "@dnd-kit/utilities";
import { PropsWithChildren } from "react";
import { RxDragHandleDots2 } from "react-icons/rx";

export const SortableItem = ({ children, id }: PropsWithChildren<{ id: number }>) => {
  const { attributes, listeners, setNodeRef, transform, transition } = useSortable({ id });

  const style = {
    transform: CSS.Transform.toString(transform),
    transition,
    touchAction: "none",
    cursor: "grab",
  };

  const { colorMode } = useColorMode();
  const themedClasses =
    colorMode === "light"
      ? "bg-slate-600 hover:bg-slate-500 text-white"
      : "bg-black hover:bg-slate-900 text-white ring-1 ring-white/30 ring-inset hover:ring-slate-200/50";

  return (
    <li
      className={`grid grid-cols-[min-content_1fr] items-center rounded-lg shadow-md gap-x-2 p-2 ${themedClasses}`}
      ref={setNodeRef}
      style={style}
      {...attributes}
      {...listeners}
    >
      <Button justifyContent="center" variant="ghost">
        <RxDragHandleDots2 />
      </Button>
      {children}
    </li>
  );
};
