import { Box, Text, useColorModeValue } from "@chakra-ui/react";
import NextLink from "next/link";
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
      <Box display="flex" flexDirection="column" alignItems="center" gap="8" fontSize="lg">
        <props.icon size="30" color="DarkOrange" />
        <Text>{props.text}</Text>
        <NextLink href="/dashboard">
          <Text color="blue.500">Go back to the dashboard</Text>
        </NextLink>
      </Box>
    </Box>
  );
};

export const TaskEmptyState = () => {
  return <EmptyState text="Looks like no tasks were found." icon={FiAlertTriangle} />;
};
