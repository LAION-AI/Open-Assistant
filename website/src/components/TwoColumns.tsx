import { Container, useColorModeValue } from "@chakra-ui/react";

export const TwoColumns = ({ children }: { children: React.ReactNode[] }) => {
  if (!Array.isArray(children) || children.length !== 2) {
    throw new Error("TwoColumns expects 2 children");
  }
  const bg = useColorModeValue("white", "gray.700");
  const [first, second] = children;

  return (
    <Container className="mb-8 lt-lg:mb-12 grid lg:gap-x-12 lg:grid-cols-2">
      <Container bg={bg} className="rounded-lg shadow-lg h-full block p-6">
        {first}
      </Container>
      <Container bg={bg} className="rounded-lg shadow-lg h-full block p-6 mt-6 lg:mt-0">
        {second}
      </Container>
    </Container>
  );
};
