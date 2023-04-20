import { Box, BoxProps } from "@chakra-ui/react";
import { LucideIcon } from "lucide-react";

export const ChatInputIconButton = ({ icon: Icon, ...props }: { icon: LucideIcon } & BoxProps) => (
  <Box
    as="button"
    color="gray.500"
    _light={{
      _hover: { color: "gray.700" },
    }}
    _dark={{
      _hover: { color: "white" },
    }}
    {...props}
    type="button"
  >
    <Icon size="20px"></Icon>
  </Box>
);
