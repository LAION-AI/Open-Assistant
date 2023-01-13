import { Box, useColorModeValue } from "@chakra-ui/react";
import { useSortable } from "@dnd-kit/sortable";
import { CSS } from "@dnd-kit/utilities";
import { PropsWithChildren, useState } from "react";
import { RxDragHandleDots2 } from "react-icons/rx";

export const SortableItem = ({
  children,
  id,
  index,
  isEditable,
  isDisabled,
}: PropsWithChildren<{ id: number; index: number; isEditable: boolean; isDisabled: boolean }>) => {
  const backgroundColor = useColorModeValue("gray.700", "gray.500");
  const disabledBackgroundColor = useColorModeValue("gray.400", "gray.700");
  const textColor = useColorModeValue("white", "white");

  const { attributes, listeners, setNodeRef, transform, transition } = useSortable({ id, disabled: !isEditable });

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
      bg={isDisabled ? disabledBackgroundColor : backgroundColor}
      borderRadius="lg"
      p="4"
      color={textColor}
      cursor={isEditable ? (grabbing ? "grabbing" : "grab") : "auto"}
      onMouseDown={() => {
        setGrabbing(true);
      }}
      onMouseUp={() => setGrabbing(false)}
      {...attributes}
      {...listeners}
      ref={setNodeRef}
      style={style}
      shadow="base"
    >
      <Box pr="4">{isEditable ? <RxDragHandleDots2 size="20px" /> : `${index + 1}.`}</Box>
      {children}
    </Box>
  );
};
