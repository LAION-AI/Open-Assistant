import {
  Box,
  Flex,
  GridItem,
  Heading,
  IconButton,
  Link as ExternalLink,
  SimpleGrid,
  Spacer,
  Text,
  useColorModeValue,
} from "@chakra-ui/react";
import { HelpCircle } from "lucide-react";
import Link from "next/link";
import { useTranslation } from "next-i18next";
import { useMemo } from "react";
import { normalizei18nKey } from "src/lib/i18n";
import { TaskType } from "src/types/Task";

import { TaskCategory, TaskCategoryLabels, TaskInfo, TaskInfos } from "../Tasks/TaskTypes";

export interface TasksOptionProps {
  content: Partial<Record<TaskCategory, TaskType[]>>;
}

export const TaskOption = ({ content }: TasksOptionProps) => {
  const { t } = useTranslation(["dashboard", "tasks"]);
  const backgroundColor = useColorModeValue("white", "gray.700");

  const taskInfoMap = useMemo(
    () =>
      Object.values(content)
        .flat()
        .reduce((obj, taskType) => {
          obj[taskType] = TaskInfos.filter((t) => t.type === taskType).pop();
          return obj;
        }, {} as Record<TaskType, TaskInfo>),
    [content]
  );

  return (
    <Box className="flex flex-col gap-14">
      {Object.entries(content).map(([category, taskTypes]) => (
        <div key={category}>
          <Flex>
            <Heading size="lg" className="pb-4">
              {t(TaskCategoryLabels[category])}
            </Heading>
            <Spacer />
            <ExternalLink href="https://projects.laion.ai/Open-Assistant/" isExternal>
              <IconButton variant="ghost" aria-label="More Information" icon={<HelpCircle size="2em" />} />
            </ExternalLink>
          </Flex>
          <SimpleGrid columns={[1, 1, 2, 2, 3, 4]} gap={4}>
            {taskTypes
              .map((taskType) => taskInfoMap[taskType])
              .map((item) => (
                <Link key={category + item.id} href={item.pathname}>
                  <GridItem
                    bg={backgroundColor}
                    borderRadius="xl"
                    boxShadow="base"
                    className="flex flex-col justify-between h-full"
                  >
                    <Flex className="p-6 pb-10" flexDir="column" gap="3">
                      <Heading size="md">{t(normalizei18nKey(`tasks:${item.id}.label`))}</Heading>
                      <Text size="sm">{t(normalizei18nKey(`tasks:${item.id}.desc`))}</Text>
                    </Flex>
                    <Text
                      fontWeight="bold"
                      color="white"
                      borderBottomRadius="xl"
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
  [TaskCategory.Random]: [TaskType.random],
  [TaskCategory.Create]: [TaskType.initial_prompt, TaskType.prompter_reply, TaskType.assistant_reply],
  [TaskCategory.Evaluate]: [
    TaskType.rank_initial_prompts,
    TaskType.rank_prompter_replies,
    TaskType.rank_assistant_replies,
  ],
  [TaskCategory.Label]: [TaskType.label_initial_prompt, TaskType.label_prompter_reply, TaskType.label_assistant_reply],
};
