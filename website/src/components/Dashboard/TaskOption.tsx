import { Box, Card, CardBody, Flex, GridItem, Heading, SimpleGrid, Text, useColorModeValue } from "@chakra-ui/react";
import Link from "next/link";
import { useMemo } from "react";
import { TaskType } from "src/types/Task";

import { TaskCategory, TaskCategoryLabels, TaskInfo, TaskInfos } from "../Tasks/TaskTypes";

export interface TasksOptionProps {
  content: Partial<Record<TaskCategory, TaskType[]>>;
}

export const TaskOption = ({ content }: TasksOptionProps) => {
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
          <Heading size="lg" className="pb-4">
            {TaskCategoryLabels[category]}
          </Heading>
          <SimpleGrid columns={[1, 1, 2, 2, 3, 4]} gap={4}>
            {taskTypes
              .map((taskType) => taskInfoMap[taskType])
              .map((item) => (
                <Link key={category + item.label} href={item.pathname}>
                  <GridItem
                    bg={backgroundColor}
                    borderRadius="xl"
                    boxShadow="base"
                    className="flex flex-col justify-between h-full"
                  >
                    <Card variant="task">
                      <CardBody>
                        <Flex flexDir="column" gap="3">
                          <Heading size="md" fontFamily="inter">
                            {item.label}
                          </Heading>
                          <Text size="sm" opacity="80%">
                            {item.desc}
                          </Text>
                        </Flex>
                      </CardBody>
                    </Card>
                    <Box
                      bg="blue.500"
                      borderBottomRadius="xl"
                      className="px-6 py-2 transition-colors duration-300"
                      _hover={{ backgroundColor: "blue.600" }}
                    >
                      <Flex className="p-6 pb-10" flexDir="column" gap="3">
                        <Heading size="md">{item.label}</Heading>
                        <Text size="sm">{item.desc}</Text>
                      </Flex>
                      <Text
                        fontWeight="bold"
                        color="white"
                        borderBottomRadius="xl"
                        className="px-6 py-2 transition-colors duration-300 bg-blue-500 hover:bg-blue-600"
                      >
                        Go -&gt;
                      </Text>
                    </Box>
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
