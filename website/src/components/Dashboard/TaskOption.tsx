import { Box, Flex, GridItem, Heading, SimpleGrid, Text, useColorModeValue } from "@chakra-ui/react";
import Link from "next/link";

import { taskTypes } from "../Tasks/TaskTypes";

function capitalize(text: string) {
  return text
    .split("_")
    .map((word: string) => word[0].toUpperCase() + word.substring(1))
    .join(" ");
}

export const TaskOption = () => {
  const backgroundColor = useColorModeValue("white", "gray.700");

  return (
    <Box className="flex flex-col gap-14" fontFamily="inter">
      {Object.keys(taskTypes).map((taskType, taskTypeIndex) => (
        <div key={taskTypeIndex}>
          <Text className="text-2xl font-bold pb-4">{capitalize(taskType)}</Text>
          <SimpleGrid columns={[1, 2, 2, 3, 4]} gap={4}>
            {Object.keys(taskTypes[taskType]).map((task, taskIndex) => (
              <Link key={taskIndex} href={`/tasks/${taskType}/${task}`}>
                <GridItem
                  bg={backgroundColor}
                  borderRadius="xl"
                  boxShadow="base"
                  className="flex flex-col justify-between h-full"
                >
                  <Box className="p-6 pb-10">
                    <Flex flexDir="column" gap="3">
                      <Heading size="md" fontFamily="inter">
                        {taskTypes[taskType][task].label}
                      </Heading>
                      <Text size="sm" opacity="80%">
                        {taskTypes[taskType][task].desc}
                      </Text>
                    </Flex>
                  </Box>
                  <Box
                    bg="blue.500"
                    borderBottomRadius="xl"
                    className="px-6 py-2 transition-colors duration-300"
                    _hover={{ backgroundColor: "blue.600" }}
                  >
                    <Text fontWeight="bold" color="white">
                      Go
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
