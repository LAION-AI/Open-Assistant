import { Box, Flex, GridItem, Heading, SimpleGrid, Text, useColorModeValue } from "@chakra-ui/react";
import Link from "next/link";

const crTasks = [
  {
    label: "Reply as User",
    desc: "Chat with Open Assistant and help improve it’s responses as you interact with it.",
    type: "create",
    pathname: "/create/assistant_reply",
  },
  {
    label: "Reply as Assistant",
    desc: "Help Open Assistant improve its responses to conversations with other users.",
    type: "create",
    pathname: "/create/assistant_reply",
  },
];

const evTasks = [
  {
    label: "Rank User Replies",
    type: "eval",
    desc: "Help Open Assistant improve its responses to conversations with other users.",
    pathname: "/evaluate/rank_user_replies",
  },

  {
    label: "Rank Assistant Replies",
    desc: "Score prompts given by Open Assistant based on their accuracy and readability.",
    type: "eval",
    pathname: "/evaluate/rank_assistant_replies",
  },
  {
    label: "Rank Initial Prompts",
    desc: "Score prompts given by Open Assistant based on their accuracy and readability.",
    type: "eval;",
    pathname: "/evaluate/rank_initial_prompts",
  },
];

export const TaskOption = () => {
  const backgroundColor = useColorModeValue("white", "gray.700");

  return (
    <Box className="flex flex-col gap-14" fontFamily="inter">
      <div>
        <Text className="text-2xl font-bold pb-4">Create</Text>
        <SimpleGrid columns={[1, 2, 2, 3, 4]} gap={4}>
          {crTasks.map((item, itemIndex) => (
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
      <div>
        <Text className="text-2xl font-bold pb-4">Evaluate</Text>
        <SimpleGrid columns={[1, 2, 2, 3, 4]} gap={4}>
          {evTasks.map((item, itemIndex) => (
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
    </Box>
  );
};
