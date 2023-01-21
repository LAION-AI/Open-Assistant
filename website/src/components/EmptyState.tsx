import { Box, Link, Text, useColorModeValue } from "@chakra-ui/react";
import { useRouter } from "next/router";
import { FiAlertTriangle } from "react-icons/fi";
import { IconType } from "react-icons/lib";

type EmptyStateProps = {
  text: string;
  icon: IconType;
};

export const EmptyState = (props: EmptyStateProps) => {
  const backgroundColor = useColorModeValue("white", "gray.800");
  const router = useRouter();

  return (
    <Box bg={backgroundColor} p="10" borderRadius="xl" shadow="base">
      <Box display="flex" flexDirection="column" alignItems="center" gap="8" fontSize="lg">
        <props.icon size="30" color="DarkOrange" />
        <Text>{props.text}</Text>
        <Link onClick={() => router.back()} color="blue.500" textUnderlineOffset="3px">
          <Text>Click here to go back</Text>
        </Link>
      </Box>
    </Box>
  );
};

export const TaskEmptyState = () => {
  return <EmptyState text="Looks like no tasks were found." icon={FiAlertTriangle} />;
};
