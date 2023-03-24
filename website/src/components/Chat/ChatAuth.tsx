import { Button, Card, CardBody, Grid, Text } from "@chakra-ui/react";
import { Github } from "lucide-react";
import Link from "next/link";
import { useSession } from "next-auth/react";
import { useTranslation } from "next-i18next";
import { useMemo } from "react";
import { Discord } from "src/components/Icons/Discord";

export const ChatAuth = ({ inferenceHost }: { inferenceHost: string }) => {
  const { t } = useTranslation(["chat", "common"]);
  const { data: session } = useSession();
  const isAuth = session?.inference.isAuthenticated;

  const content = useMemo(() => {
    if (isAuth) {
      return (
        <CardBody display="flex" flexDirection="row" justifyContent="space-between" alignItems="center" gap={4}>
          <Text>{t("you_are_logged_in")}</Text>
          <Button>{t("common:sign_out")}</Button>
        </CardBody>
      );
    }
    return (
      <CardBody display="flex" flexDirection="column" gap={4}>
        <Text>{t("login_message")}</Text>
        <Grid justifyItems="center" gridTemplateColumns="repeat(2, minmax(150px, 1fr))" gap={12}>
          <Link href={`${inferenceHost}/auth/login/github`}>
            <Github size={128} />
          </Link>
          <Link href={`${inferenceHost}/auth/login/discord`}>
            <Discord size={128} />
          </Link>
        </Grid>
      </CardBody>
    );
  }, [isAuth, t, inferenceHost]);

  return <Card mt={4}>{content}</Card>;
};
