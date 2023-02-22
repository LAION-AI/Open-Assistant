import {
  Badge,
  Box,
  Card,
  Flex,
  GridItem,
  Heading,
  IconButton,
  Link as ExternalLink,
  SimpleGrid,
  Spacer,
  Text,
} from "@chakra-ui/react";
import { HelpCircle } from "lucide-react";
import Link from "next/link";
import { useTranslation } from "next-i18next";
import { useMemo } from "react";
import { getTypeSafei18nKey } from "src/lib/i18n";
import { TaskCategory, TaskInfo, TaskType } from "src/types/Task";

import { TaskCategoryLabels, TaskInfos } from "../Tasks/TaskTypes";

export type TaskCategoryItem = { taskType: TaskType; count: number };

export interface TasksOptionProps {
  content: Partial<Record<TaskCategory, TaskCategoryItem[]>>;
}

export const TaskOption = ({ content }: TasksOptionProps) => {
  const { t } = useTranslation(["dashboard", "tasks"]);

  const taskInfoMap = useMemo(
    () =>
      Object.values(content)
        .flat()
        .reduce((obj, { taskType }) => {
          obj[taskType] = TaskInfos.filter((t) => t.type === taskType).pop();
          return obj;
        }, {} as Record<TaskType, TaskInfo>),
    [content]
  );

  return (
    <Box className="flex flex-col gap-14">
      {Object.entries(content).map(([category, items]) => (
        <div key={category}>
          <Flex>
            <Heading size="lg" className="pb-4">
              {t(TaskCategoryLabels[category])}
            </Heading>
            <Spacer />
            <ExternalLink href="https://projects.laion.ai/Open-Assistant/docs/guides/guidelines" isExternal>
              <IconButton variant="ghost" aria-label="More Information" icon={<HelpCircle size="2em" />} />
            </ExternalLink>
          </Flex>
          <SimpleGrid columns={[1, 1, 2, 2, 3, 4]} gap={4}>
            {items
              .map(({ taskType, count }) => ({ ...taskInfoMap[taskType], count }))
              .map((item) => (
                <Link key={category + item.id} href={item.pathname}>
                  <GridItem as={Card} height="100%" justifyContent="space-between">
                    <Flex px="6" pt="6" flexDir="column" gap="3" justifyContent="space-between" height="100%">
                      <Flex flexDir="column" gap="3">
                        <Heading size="md">{t(getTypeSafei18nKey(`tasks:${item.id}.label`))}</Heading>
                        <Text size="sm">{t(getTypeSafei18nKey(`tasks:${item.id}.desc`))}</Text>
                      </Flex>
                      <Box>
                        <Badge textTransform="none">{t("tasks:available_task_count", { count: item.count })}</Badge>
                      </Box>
                    </Flex>
                    <Text
                      fontWeight="bold"
                      color="white"
                      borderBottomRadius="xl"
                      mt="6"
                      className="px-6 py-2 transition-colors duration-300 bg-blue-500 hover:bg-blue-600"
                    >
                      {t("go")} -&gt;
                    </Text>
                  </GridItem>
                </Link>
              ))}
          </SimpleGrid>
        </div>
      ))}
    </Box>
  );
};

export const allTaskOptions: TasksOptionProps["content"] = {
  [TaskCategory.Random]: [{ taskType: TaskType.random, count: 0 }],
  [TaskCategory.Create]: [
    { taskType: TaskType.initial_prompt, count: 0 },
    { taskType: TaskType.prompter_reply, count: 0 },
    { taskType: TaskType.assistant_reply, count: 0 },
  ],
  [TaskCategory.Evaluate]: [
    { taskType: TaskType.rank_initial_prompts, count: 0 },
    { taskType: TaskType.rank_prompter_replies, count: 0 },
    { taskType: TaskType.rank_assistant_replies, count: 0 },
  ],
  [TaskCategory.Label]: [
    { taskType: TaskType.label_initial_prompt, count: 0 },
    { taskType: TaskType.label_prompter_reply, count: 0 },
    { taskType: TaskType.label_assistant_reply, count: 0 },
  ],
};
