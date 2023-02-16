import { useColorMode } from "@chakra-ui/react";
import { Turnstile, TurnstileInstance, TurnstileProps } from "@marsidev/react-turnstile";
import { forwardRef } from "react";

export const CloudFlareCaptcha = forwardRef<TurnstileInstance, TurnstileProps>((props, ref) => {
  const { siteKey, ...restProps } = props;
  const { colorMode } = useColorMode();
  return (
    <Turnstile
      ref={ref}
      {...restProps}
      siteKey={siteKey}
      options={{
        theme: colorMode,
        ...props.options,
      }}
    />
  );
});

CloudFlareCaptcha.displayName = "CloudFlareCaptcha";
