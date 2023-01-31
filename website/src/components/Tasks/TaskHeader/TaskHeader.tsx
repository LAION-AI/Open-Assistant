import { HStack, IconButton, Link, Stack, Text, useColorModeValue } from "@chakra-ui/react";
import { HelpCircle } from "lucide-react";
import { useTranslation } from "next-i18next";
import { getTypeSafei18nKey } from "src/lib/i18n";
import { TaskInfo } from "src/types/Task";

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
  const { t } = useTranslation(["tasks", "common"]);
  const labelColor = useColorModeValue("gray.600", "gray.400");
  const titleColor = useColorModeValue("gray.800", "gray.300");
  return (
    <Stack spacing="1">
      <HStack>
        <Text fontSize="xl" fontWeight="bold" color={titleColor}>
          {t(getTypeSafei18nKey(`${taskType.id}.label`))}
        </Text>
        <Link href={taskType.help_link} isExternal>
          <IconButton variant="ghost" aria-label="More Information" icon={<HelpCircle size="1em" />} />
        </Link>
      </HStack>
      <Text fontSize="md" color={labelColor}>
        {t(getTypeSafei18nKey(`${taskType.id}.overview`))}
      </Text>
    </Stack>
  );
};

export { TaskHeader };
