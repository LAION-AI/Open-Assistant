import { Box, Text, useColorModeValue } from "@chakra-ui/react";
import { FiAlertTriangle } from "react-icons/fi";
import { IconType } from "react-icons/lib";

type EmptyStateProps = {
  text: string;
  icon: IconType;
};

export const EmptyState = (props: EmptyStateProps) => {
  const backgroundColor = useColorModeValue("white", "gray.800");

  return (
    <Box bg={backgroundColor} p="10" borderRadius="xl" shadow="base">
      <Box display="flex" flexDirection="column" alignItems="center" gap="8">
        <props.icon size="30" color="DarkOrange" />
        <Text fontSize="lg">{props.text}</Text>
      </Box>
    </Box>
  );
};

export const TaskEmptyState = () => {
  return <EmptyState text="Looks like no tasks were found." icon={FiAlertTriangle} />;
};
