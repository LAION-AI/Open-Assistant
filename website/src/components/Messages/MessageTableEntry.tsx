import { Avatar, Box, HStack, useColorModeValue } from "@chakra-ui/react";

import { FlaggableElement } from "../FlaggableElement";

export function MessageTableEntry ({ item, idx }) {
    const bgColor = useColorModeValue(idx % 2 === 0 ? "bg-slate-800" : "bg-black", "bg-sky-900");
  
    return (
      <FlaggableElement text={item.text} post_id={item.id} key={`flag_${item.id}`}>
        <HStack>
          <Avatar
            name={`${item.isAssistant ? "Assitant" : "User"}`}
            src={`${item.isAssistant ? "/logos/logo.png" : "/images/temp-avatars/av1.jpg"}`}
          />
          <Box className={`p-4 rounded-md text-white whitespace-pre-wrap ${bgColor} text-white w-full`}>{item.text}</Box>
        </HStack>
      </FlaggableElement>
    );
  };