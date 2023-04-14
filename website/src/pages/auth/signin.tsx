import {
  Box,
  Button,
  ButtonProps,
  FormControl,
  FormErrorMessage,
  Input,
  Stack,
  useColorModeValue,
} from "@chakra-ui/react";
import { useColorMode } from "@chakra-ui/react";
import { SiDiscord, SiGoogle } from "@icons-pack/react-simple-icons";
import { TurnstileInstance } from "@marsidev/react-turnstile";
import { boolean } from "boolean";
import { Bug, Mail } from "lucide-react";
import { GetServerSideProps } from "next";
import Head from "next/head";
import Link from "next/link";
import { useRouter } from "next/router";
import { BuiltInProviderType } from "next-auth/providers";
import { ClientSafeProvider, getProviders, signIn } from "next-auth/react";
import { serverSideTranslations } from "next-i18next/serverSideTranslations";
import React, { useEffect, useRef, useState } from "react";
import { useForm } from "react-hook-form";
import { AuthLayout } from "src/components/AuthLayout";
import { CloudFlareCaptcha } from "src/components/CloudflareCaptcha";
import { Role, RoleSelect } from "src/components/RoleSelect";

export type SignInErrorTypes =
  | "Signin"
  | "OAuthSignin"
  | "OAuthCallback"
  | "OAuthCreateAccount"
  | "EmailCreateAccount"
  | "Callback"
  | "OAuthAccountNotLinked"
  | "EmailSignin"
  | "CredentialsSignin"
  | "SessionRequired"
  | "InvalidCaptcha"
  | "default";

const errorMessages: Record<SignInErrorTypes, string> = {
  Signin: "Try signing in with a different account.",
  OAuthSignin: "Try signing in with a different account.",
  OAuthCallback: "Try signing in with the same account you used originally.",
  OAuthCreateAccount: "Try signing in with a different account.",
  EmailCreateAccount: "Try signing in with a different account.",
  Callback: "Try signing in with a different account.",
  OAuthAccountNotLinked: "To confirm your identity, sign in with the same account you used originally.",
  EmailSignin: "The e-mail could not be sent.",
  CredentialsSignin: "Sign in failed. Check the details you provided are correct.",
  SessionRequired: "Please sign in to access this page.",
  InvalidCaptcha: "Invalid captcha",
  default: "Unable to sign in.",
};

interface SigninProps {
  providers: Record<BuiltInProviderType, ClientSafeProvider>;
  enableEmailSignin: boolean;
  enableEmailSigninCaptcha: boolean;
  cloudflareCaptchaSiteKey: string;
}

function Signin({ providers, enableEmailSignin, enableEmailSigninCaptcha, cloudflareCaptchaSiteKey }: SigninProps) {
  const router = useRouter();
  const { discord, email, google, credentials } = providers;
  const [error, setError] = useState("");

  useEffect(() => {
    const err = router?.query?.error;
    if (err) {
      if (typeof err === "string") {
        setError(errorMessages[err as SignInErrorTypes]);
      } else {
        setError(errorMessages[err[0] as SignInErrorTypes]);
      }
    }
  }, [router]);

  const { colorMode } = useColorMode();
  const buttonBgColor = colorMode === "light" ? "#2563eb" : "#2563eb";

  return (
    <>
      <Head>
        <title>Sign Up - Open Assistant</title>
        <meta name="Sign Up" content="Sign up to access Open Assistant" />
      </Head>
      <AuthLayout>
        <Stack spacing="2">
          {credentials && <DebugSigninForm providerId={credentials.id} />}
          {email && enableEmailSignin && (
            <EmailSignInForm
              providerId={email.id}
              enableEmailSigninCaptcha={enableEmailSigninCaptcha}
              cloudflareCaptchaSiteKey={cloudflareCaptchaSiteKey}
            />
          )}
          {discord && (
            <Button
              bg={buttonBgColor}
              _hover={{ bg: "#4A57E3" }}
              _active={{ bg: "#454FBF" }}
              size="lg"
              color="white"
              leftIcon={<SiDiscord />}
              onClick={() => signIn(discord.id, { callbackUrl: "/" })}
            >
              Continue with Discord
            </Button>
          )}
          {google && (
            <Button
              bg={buttonBgColor}
              _hover={{ bg: "#4A57E3" }}
              _active={{ bg: "#454FBF" }}
              size="lg"
              color="white"
              leftIcon={<SiGoogle />}
              onClick={() => signIn(google.id, { callbackUrl: "/" })}
            >
              Continue with Google
            </Button>
          )}
        </Stack>
        <hr className="mt-14 mb-4 h-px bg-gray-200 border-0" />
        <div className="text-center">
          By signing up you agree to our <br></br>
          <Link href="/terms-of-service" aria-label="Terms of Service" className="hover:underline underline-offset-4">
            <b>Terms of Service</b>
          </Link>{" "}
          and{" "}
          <Link href="/privacy-policy" aria-label="Privacy Policy" className="hover:underline underline-offset-4">
            <b>Privacy Policy</b>
          </Link>
          .
        </div>
        {error && (
          <div className="text-center mt-8">
            <p className="text-orange-600">Error: {error}</p>
          </div>
        )}
      </AuthLayout>
    </>
  );
}

export default Signin;

const EmailSignInForm = ({
  providerId,
  enableEmailSigninCaptcha,
  cloudflareCaptchaSiteKey,
}: {
  providerId: string;
  enableEmailSigninCaptcha: boolean;
  cloudflareCaptchaSiteKey: string;
}) => {
  const {
    register,
    formState: { errors },
    handleSubmit,
  } = useForm<{ email: string }>();
  const captcha = useRef<TurnstileInstance>(null);
  const [captchaSuccess, setCaptchaSuccess] = useState(false);
  const signinWithEmail = (data: { email: string }) => {
    signIn(providerId, {
      callbackUrl: "/dashboard",
      email: data.email,
      captcha: captcha.current?.getResponse(),
    });
  };
  return (
    <form onSubmit={handleSubmit(signinWithEmail)}>
      <Stack>
        <FormControl isInvalid={errors.email ? true : false}>
          <Input
            type="email"
            data-cy="email-address"
            variant="outline"
            size="lg"
            placeholder="Email Address"
            {...register("email", { required: true, pattern: /[^\s@]+@[^\s@]+\.[^\s@]+/g })}
            errorBorderColor="orange.600"
          />
          <FormErrorMessage>
            {errors.email?.type === "required" && "Email is required"}
            {errors.email?.type === "pattern" && "Email is invalid"}
          </FormErrorMessage>
        </FormControl>
        {enableEmailSigninCaptcha && (
          <CloudFlareCaptcha
            siteKey={cloudflareCaptchaSiteKey}
            options={{ size: "invisible" }}
            ref={captcha}
            onSuccess={() => setCaptchaSuccess(true)}
          ></CloudFlareCaptcha>
        )}
        <SigninButton
          data-cy="signin-email-button"
          leftIcon={<Mail />}
          mt="4"
          isDisabled={!captchaSuccess && enableEmailSigninCaptcha}
        >
          Continue with Email
        </SigninButton>
      </Stack>
    </form>
  );
};

const SigninButton = (props: ButtonProps) => {
  const buttonColorScheme = useColorModeValue("blue", "dark-blue-btn");

  return (
    <Button
      size={"lg"}
      leftIcon={<Mail />}
      type="submit"
      colorScheme={buttonColorScheme}
      color="white"
      {...props}
    ></Button>
  );
};

interface DebugSigninFormData {
  username: string;
  role: Role;
}

const DebugSigninForm = ({ providerId }: { providerId: string }) => {
  const { register, handleSubmit } = useForm<DebugSigninFormData>({
    defaultValues: {
      role: "general",
      username: "dev",
    },
  });

  function signinWithDebugCredentials(data: DebugSigninFormData) {
    signIn(providerId, {
      callbackUrl: "/dashboard",
      ...data,
    });
  }
  const bgColorClass = useColorModeValue("gray.50", "gray.900");

  return (
    <form
      onSubmit={handleSubmit(signinWithDebugCredentials)}
      className="border-2 border-orange-600 rounded-md p-4 relative"
    >
      <Box bg={bgColorClass} className={`text-orange-600 absolute -top-3 left-5 px-1 z-20`}>
        For Debugging Only
      </Box>
      <Stack>
        <Input
          variant="outline"
          size="lg"
          placeholder="Username"
          {...register("username")}
          errorBorderColor="orange.600"
        />
        <RoleSelect {...register("role")}></RoleSelect>
        <SigninButton leftIcon={<Bug />}>Continue with Debug User</SigninButton>
      </Stack>
    </form>
  );
};

export const getServerSideProps: GetServerSideProps<SigninProps> = async ({ locale = "en" }) => {
  const providers = (await getProviders())!;
  const enableEmailSignin = boolean(process.env.ENABLE_EMAIL_SIGNIN);
  const enableEmailSigninCaptcha = boolean(process.env.ENABLE_EMAIL_SIGNIN_CAPTCHA);
  const cloudflareCaptchaSiteKey = process.env.CLOUDFLARE_CAPTCHA_SITE_KEY;
  return {
    props: {
      providers,
      enableEmailSignin,
      enableEmailSigninCaptcha,
      cloudflareCaptchaSiteKey,
      ...(await serverSideTranslations(locale, ["common"])),
    },
  };
};
