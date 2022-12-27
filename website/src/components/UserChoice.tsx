import { Card, CardBody, Flex, Heading } from "@chakra-ui/react";
import Link from "next/link";
import React from "react";
import Image from "next/image";

const UserChoice = () => {
  return (
    <Flex gap={10} wrap="wrap" justifyContent="center">
      <Choice alt="Rate Prompts" title="Rate prompts" link="/grading/grade-output" />
      <Choice alt="Summarize Stories" title="Summarize stories" link="/summarize/story" />
    </Flex>
  );
};

type ChoiceProps = {
  img?: string;
  alt: string;
  title: string;
  link: string;
};

const Choice = (props: ChoiceProps) => {
  const { img, title, link } = props;
  // NEXT STEPS: FIND BETTER IMAGES AND USE img PROP AS SRC
  return (
    <Link href={link}>
      <Card maxW="sm" minW="sm" minH="sm" maxH="sm">
        <CardBody width="full" height="full">
          <Flex direction="column" alignItems="center" justifyContent="center">
            <Image
              className="transition ease-in-out duration-300 sm:grayscale hover:grayscale-0"
              src="/images/logos/logo.sv"
              alt="LAION Logo"
              width={500}
              height={500}
            />
            <Heading
              mt={-10}
              className="bg-gradient-to-r from-indigo-600 via-sky-400 to-indigo-700 bg-clip-text tracking-tight text-transparent"
              textAlign={"center"}
              fontSize={"4xl"}
            >
              {title}
            </Heading>
          </Flex>
        </CardBody>
      </Card>
    </Link>
  );
};

export default UserChoice;
