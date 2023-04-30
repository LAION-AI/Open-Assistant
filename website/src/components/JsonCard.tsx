import { Card, CardBody } from "@chakra-ui/card";
import { CardBodyProps, CardProps } from "@chakra-ui/react";
import { StrictOmit } from "ts-essentials";

type JsonCardProps = StrictOmit<CardProps, "children"> & {
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  children: any;
  bodyProps?: CardBodyProps;
};

export const JsonCard = ({ children, bodyProps, ...props }: JsonCardProps) => {
  return (
    <Card variant="json" {...props}>
      <CardBody overflowX="auto" {...bodyProps}>
        <pre>{JSON.stringify(children, null, 2)}</pre>
      </CardBody>
    </Card>
  );
};
