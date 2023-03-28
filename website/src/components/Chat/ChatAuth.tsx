import { Box, Button, Card, CardBody, Grid, Text } from "@chakra-ui/react";
import { Github } from "lucide-react";
import Link from "next/link";
import { useSession } from "next-auth/react";
import { useTranslation } from "next-i18next";
import { memo, ReactNode } from "react";
import { Discord } from "src/components/Icons/Discord";
import { useInferenceAuth } from "src/hooks/chat/useInferenceAuth";
import { OasstInferenceClient } from "src/lib/oasst_inference_client";
import useSWRImmutable from "swr/immutable";

const icons: Record<string, ReactNode> = {
  github: <Github size={128} />,
  discord: <Discord size={128} />,
};

export const ChatAuth = memo(function ChatAuth() {
  const { t } = useTranslation(["chat", "common"]);
  const { data: authProviders } = useSWRImmutable(
    `/auth/providers`,
    () => {
      return new OasstInferenceClient().get_providers();
    },
    {
      fallbackData: [],
    }
  );

  const { isAuthenticated, isLoading } = useInferenceAuth();

  console.log(authProviders);

  const { data: session } = useSession();
  // const isAuth = session?.inference.isAuthenticated;
  const isAuth = false;
  const username = session?.user.name;

  if (isAuthenticated) {
    return null;
  }

  if (isAuth) {
    return (
      <Card mt={4}>
        <CardBody display="flex" flexDirection="row" justifyContent="space-between" alignItems="center" gap={4}>
          <Text>{t("you_are_logged_in")}</Text>
          <Box as={Button}>
            <Link href="/api/inference_auth/logout">{t("common:sign_out")}</Link>
          </Box>
        </CardBody>
      </Card>
    );
  }
  return (
    <Card mt={4}>
      <CardBody display="flex" flexDirection="column" gap={4}>
        <Text>{t("login_message")}</Text>
        <Grid
          justifyItems="center"
          gridTemplateColumns={`repeat(${authProviders!.length}, minmax(150px, 1fr))`}
          gap={12}
        >
          {authProviders!.map((provider) => (
            <Link
              key={provider}
              href={
                `${process.env.INFERENCE_SERVER_HOST}/auth/login/${provider}` +
                (provider === "debug" ? `?username=${username}` : "")
              }
            >
              {icons[provider] ?? provider}
            </Link>
          ))}
        </Grid>
      </CardBody>
    </Card>
  );
});
