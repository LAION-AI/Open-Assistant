import { Box, Flex, Text, TextProps, useColorModeValue } from "@chakra-ui/react";

const TitleClasses: TextProps = {
  fontWeight: "semibold",
  fontSize: "md",
  cursor: "default",
};

const LabelClasses: TextProps = {
  fontSize: "sm",
  cursor: "default",
  color: "gray.500",
};

export const TaskInfo = ({ id, output }: { id: string; output: string }) => {
  const titleColor = useColorModeValue("gray.700", "gray.400");

  return (
    <Box>
      <Flex direction="column">
        <Flex alignItems="center" gap="2">
          <Text {...TitleClasses} color={titleColor}>
            Prompt
          </Text>
          <Text {...LabelClasses} data-cy="task-id">
            {id}
          </Text>
        </Flex>
        <Flex alignItems="center" gap="2">
          <Text {...TitleClasses} color={titleColor}>
            Output
          </Text>
          <Text {...LabelClasses}>{output}</Text>
        </Flex>
      </Flex>
    </Box>
  );
};
