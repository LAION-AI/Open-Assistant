import { HStack, IconButton, Link, Stack, Text, useColorModeValue } from "@chakra-ui/react";
import { FiHelpCircle } from "react-icons/fi";
import type { TaskInfo } from "src/components/Tasks/TaskTypes";

interface TaskHeaderProps {
  /**
   * The `TaskInfo` representing how we present the task to a user.
   */
  taskType: TaskInfo;
}

/**
 * Presents the Task label, instructions, and help link
 */
const TaskHeader = ({ taskType }: TaskHeaderProps) => {
  const labelColor = useColorModeValue("gray.600", "gray.400");
  const titleColor = useColorModeValue("gray.800", "gray.300");
  return (
    <Stack spacing="1">
      <HStack>
        <Text fontSize="xl" fontWeight="bold" color={titleColor}>
          {taskType.label}
        </Text>
        <Link href={taskType.help_link} isExternal>
          <IconButton variant="ghost" aria-label="More Information" icon={<FiHelpCircle />} />
        </Link>
      </HStack>
      <Text fontSize="md" color={labelColor}>
        {taskType.overview}
      </Text>
    </Stack>
  );
};

export { TaskHeader };
