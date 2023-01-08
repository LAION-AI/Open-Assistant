import { Box, Flex, GridItem, Heading, SimpleGrid, Text, useColorModeValue } from "@chakra-ui/react";
import Link from "next/link";

import { TaskCategory, TaskTypes } from "../Tasks/TaskTypes";

const displayTaskCategories = [TaskCategory.Create, TaskCategory.Evaluate, TaskCategory.Label];

export const TaskOption = () => {
  const backgroundColor = useColorModeValue("white", "gray.700");

  return (
    <Box className="flex flex-col gap-14" fontFamily="inter">
      {displayTaskCategories.map((category, categoryIndex) => (
        <div key={categoryIndex}>
          <Text className="text-2xl font-bold pb-4">{category}</Text>
          <SimpleGrid columns={[1, 2, 2, 3, 4]} gap={4}>
            {TaskTypes.filter((task) => task.category === category).map((item, itemIndex) => (
              <Link key={itemIndex} href={item.pathname}>
                <GridItem
                  bg={backgroundColor}
                  borderRadius="xl"
                  boxShadow="base"
                  className="flex flex-col justify-between h-full"
                >
                  <Box className="p-6 pb-10">
                    <Flex flexDir="column" gap="3">
                      <Heading size="md" fontFamily="inter">
                        {item.label}
                      </Heading>
                      <Text size="sm" opacity="80%">
                        {item.desc}
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
