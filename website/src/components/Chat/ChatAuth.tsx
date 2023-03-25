import { Box, Button, Card, CardBody, Grid, Text } from "@chakra-ui/react";
import { Github } from "lucide-react";
import Link from "next/link";
import { useSession } from "next-auth/react";
import { useTranslation } from "next-i18next";
import { memo } from "react";
import { Discord } from "src/components/Icons/Discord";
import { get } from "src/lib/api";
import useSWRImmutable from "swr/immutable";

const icons = {
  github: <Github size={128} />,
  discord: <Discord size={128} />,
};

export const ChatAuth = memo(function ChatAuth({ inferenceHost }: { inferenceHost: string }) {
  const { t } = useTranslation(["chat", "common"]);
  const { data: authProviders } = useSWRImmutable<string[]>(`${inferenceHost}/auth/providers`, get, {
    fallbackData: [],
  });

  const { data: session } = useSession();
  const isAuth = session?.inference.isAuthenticated;
  const username = session?.user.name;

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
          gridTemplateColumns={`repeat(${authProviders.length}, minmax(150px, 1fr))`}
          gap={12}
        >
          {authProviders.map((provider) => (
            <Link
              key={provider}
              href={`${inferenceHost}/auth/login/${provider}` + (provider === "debug" ? `?username=${username}` : "")}
            >
              {icons[provider] ?? provider}
            </Link>
          ))}
        </Grid>
      </CardBody>
    </Card>
  );
});
