import { Card, CardBody } from "@chakra-ui/card";

// eslint-disable-next-line @typescript-eslint/no-explicit-any
export const JsonCard = ({ children }: { children: any }) => {
  return (
    <Card variant="json">
      <CardBody overflowX="auto">
        <pre>{JSON.stringify(children, null, 2)}</pre>
      </CardBody>
    </Card>
  );
};
