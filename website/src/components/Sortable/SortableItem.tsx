import { Box, useColorModeValue } from "@chakra-ui/react";
import { useSortable } from "@dnd-kit/sortable";
import { CSS } from "@dnd-kit/utilities";
import { GripVertical } from "lucide-react";
import { PropsWithChildren, useMemo } from "react";

export const SortableItem = ({
  children,
  id,
  index,
  isEditable,
  isDisabled,
}: PropsWithChildren<{ id: number; index: number; isEditable: boolean; isDisabled: boolean }>) => {
  const backgroundColor = useColorModeValue("gray.700", "gray.500");
  const disabledBackgroundColor = useColorModeValue("gray.400", "gray.700");
  const activeBackgroundColor = useColorModeValue("gray.600", "gray.600");
  const textColor = useColorModeValue("white", "white");

  const { attributes, listeners, setNodeRef, transform, transition } = useSortable({ id, disabled: !isEditable });

  const sx = useMemo(
    () => ({
      "&:active": {
        bg: `${isEditable ? activeBackgroundColor : backgroundColor}`,
        cursor: `${isEditable ? "grabbing" : "default"}`,
      },
      touchAction: "none",
    }),
    [isEditable, activeBackgroundColor, backgroundColor]
  );

  return (
    <Box
      sx={sx}
      transform={CSS.Translate.toString(transform)}
      transition={transition}
      display="flex"
      alignItems="center"
      bg={isDisabled ? disabledBackgroundColor : backgroundColor}
      borderRadius="lg"
      p="4"
      whiteSpace="pre-wrap"
      color={textColor}
      aria-roledescription="sortable"
      ref={setNodeRef}
      shadow="base"
      {...attributes}
      {...listeners}
    >
      <Box pr="4">{isEditable ? <GripVertical size="20px" /> : `${index + 1}.`}</Box>
      {children}
    </Box>
  );
};
