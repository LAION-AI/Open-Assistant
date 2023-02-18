import { Box, Text, useColorModeValue } from "@chakra-ui/react";
import { AlertTriangle, LucideIcon } from "lucide-react";
import NextLink from "next/link";
import { useTranslation } from "next-i18next";

type EmptyStateProps = {
  text: string;
  icon: LucideIcon;
  "data-cy"?: string;
};

export const EmptyState = (props: EmptyStateProps) => {
  const backgroundColor = useColorModeValue("white", "gray.800");

  const { t } = useTranslation("common");

  return (
    <Box data-cy={props["data-cy"]} bg={backgroundColor} p="10" borderRadius="xl" shadow="base">
      <Box display="flex" flexDirection="column" alignItems="center" gap="8" fontSize="lg">
        <props.icon size="30" color="DarkOrange" />
        <Text data-cy="cy-no-tasks">{props.text}</Text>
        <NextLink href="/dashboard">
          <Text color="blue.500">{t("back_to_dashboard")}</Text>
        </NextLink>
      </Box>
    </Box>
  );
};

export const TaskEmptyState = () => {
  const { t } = useTranslation("tasks");

  return <EmptyState text={t("no_more_tasks")} icon={AlertTriangle} data-cy="task" />;
};
