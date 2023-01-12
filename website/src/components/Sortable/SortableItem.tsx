import { Box, useColorModeValue } from "@chakra-ui/react";
import { useSortable } from "@dnd-kit/sortable";
import { CSS } from "@dnd-kit/utilities";
import { PropsWithChildren, useState } from "react";
import { RxDragHandleDots2 } from "react-icons/rx";

export const SortableItem = ({ children, id }: PropsWithChildren<{ id: number }>) => {
  const backgroundColor = useColorModeValue("gray.700", "gray.500");
  const textColor = useColorModeValue("white", "white");

  const { attributes, listeners, setNodeRef, transform, transition } = useSortable({ id });

  const style = {
    transform: CSS.Translate.toString(transform),
    transition,
    touchAction: "none",
  };

  const [grabbing, setGrabbing] = useState(false);

  return (
    <Box
      display="flex"
      alignItems="center"
      bg={backgroundColor}
      borderRadius="lg"
      p="4"
      color={textColor}
      cursor={grabbing ? "grabbing" : "grab"}
      onMouseDown={() => setGrabbing(true)}
      onMouseUp={() => setGrabbing(false)}
      {...attributes}
      {...listeners}
      ref={setNodeRef}
      style={style}
      shadow="base"
    >
      <Box pr="4">
        <RxDragHandleDots2 size="20px" />
      </Box>
      {children}
    </Box>
  );
};
