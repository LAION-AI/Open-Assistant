<<<<<<< HEAD
import { ArrowDownIcon, ArrowUpIcon } from "@heroicons/react/20/solid";
=======
>>>>>>> main
import { Button } from "@chakra-ui/react";
import { useSortable } from "@dnd-kit/sortable";
import { CSS } from "@dnd-kit/utilities";
import { RxDragHandleDots2 } from "react-icons/rx";
import { PropsWithChildren } from "react";

export const SortableItem = ({ children, id }: PropsWithChildren<{ id: number }>) => {
  const { attributes, listeners, setNodeRef, transform, transition } = useSortable({ id });

  const style = {
    transform: CSS.Transform.toString(transform),
    transition,
    touchAction: "none",
  };

  return (
    <li
      className="grid grid-cols-[min-content_1fr] items-center rounded-lg shadow-md gap-x-2 p-2 bg-white hover:bg-slate-50"
      ref={setNodeRef}
      style={style}
    >
      <Button justifyContent="center" variant="ghost" {...attributes} {...listeners}>
        <RxDragHandleDots2 />
      </Button>
      {children}
    </li>
  );
};
