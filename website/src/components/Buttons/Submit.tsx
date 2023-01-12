import { Button, ButtonProps } from "@chakra-ui/react";

export const SubmitButton = ({ children, ...props }: ButtonProps) => {
  return (
    <Button size="lg" variant="solid" {...props}>
      {children}
    </Button>
  );
};
