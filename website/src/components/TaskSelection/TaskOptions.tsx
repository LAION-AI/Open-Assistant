import { Divider, Flex, Heading } from "@chakra-ui/react";
import React from "react";

export type TaskOptionsProps = {
  title: string;
  children: JSX.Element | JSX.Element[];
};

export const TaskOptions = (props: TaskOptionsProps) => {
  const { title, children } = props;
  return (
    <Flex gap={10} wrap="wrap" justifyContent="center">
      <Heading
        className="bg-gradient-to-r from-indigo-600 via-sky-400 to-indigo-700 bg-clip-text tracking-tight text-transparent"
        fontSize="5xl"
      >
        {title}
      </Heading>
      <Divider mt={-8} />
      {children}
    </Flex>
  );
};
