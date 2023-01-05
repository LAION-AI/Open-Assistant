import { Button, ButtonProps } from "@chakra-ui/react";

export const SocialLoginButton = ({ children, ...props }: ButtonProps) => {
    return (
        <Button {...props}>
            {children}
        </Button>
    )
}
