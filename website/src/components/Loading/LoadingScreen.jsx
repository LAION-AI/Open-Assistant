import { Container, Progress } from "@chakra-ui/react";

export const LoadingScreen = ({ text }) => (
  <Container>
    <Progress size="xs" isIndeterminate />
    {text && (
      <Container className="flex h-full">
        <div className="text-xl font-bold text-gray-800  mx-auto my-auto">{text}</div>
      </Container>
    )}
  </Container>
);
