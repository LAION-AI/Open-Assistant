import { Button, ButtonProps } from "@chakra-ui/react";

export const SkipButton = ({ children, ...props }: ButtonProps) => {
  return (
    <Button size="lg" variant="outline" {...props}>
      {children}
    </Button>
  );
};
