import { Box, Flex, useColorModeValue } from "@chakra-ui/react";
import { SyntheticListenerMap } from "@dnd-kit/core/dist/hooks/utilities";
import { useSortable } from "@dnd-kit/sortable";
import { CSS } from "@dnd-kit/utilities";
import { GripVertical } from "lucide-react";
import { PointerEventHandler, PropsWithChildren, useMemo } from "react";

import { MessageSyntheticBadge } from "../Messages/MessageSyntheticBadge";

export const SortableItem = ({
  children,
  id,
  index,
  isEditable,
  isDisabled,
  OpenModal,
  synthetic,
}: PropsWithChildren<{
  id: number;
  index: number;
  isEditable: boolean;
  isDisabled: boolean;
  OpenModal: () => void;
  synthetic: boolean | null;
}>) => {
  const backgroundColor = useColorModeValue("gray.700", "gray.500");
  const disabledBackgroundColor = useColorModeValue("gray.400", "gray.700");
  const activeBackgroundColor = useColorModeValue("gray.600", "gray.600");
  const textColor = useColorModeValue("white", "white");

  const { attributes, listeners, setNodeRef, transform, transition } = useSortable({ id, disabled: !isEditable });
  const pcListeners = { onKeyDown: listeners?.onKeyDown, onMouseDown: listeners?.onMouseDown } as SyntheticListenerMap;
  const sx = useMemo(
    () => ({
      "&:active": {
        bg: `${isEditable ? activeBackgroundColor : backgroundColor}`,
        cursor: `${isEditable ? "grabbing" : "default"}`,
      },
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
      ref={setNodeRef}
      shadow="base"
      {...attributes}
      {...pcListeners}
      aria-roledescription="sortable"
      className="relative"
    >
      <Box pr="4">{isEditable ? <GripVertical size="20px" /> : `${index + 1}.`}</Box>
      {children}
      <div
        onClick={OpenModal}
        onPointerDown={listeners?.onPointerDown as PointerEventHandler<HTMLDivElement>}
        className="w-[67%] lg:w-[80%]  h-full  absolute ltr:left-0 rtl:right-0 top-0 touch-none"
      ></div>
      <Flex
        position="absolute"
        gap="2"
        top="-2.5"
        style={{
          insetInlineEnd: "1.25rem",
        }}
      >
        {synthetic && <MessageSyntheticBadge />}
      </Flex>
    </Box>
  );
};
