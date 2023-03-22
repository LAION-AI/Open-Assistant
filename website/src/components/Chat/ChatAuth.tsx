import { Card, CardBody, Grid, Text } from "@chakra-ui/react";
import { Github } from "lucide-react";
import Link from "next/link";
import { useTranslation } from "next-i18next";
import { Discord } from "src/components/Icons/Discord";

const inferenceHost = process.env.NEXT_PUBLIC_INFERENCE_SERVER_HOST;

export const ChatAuth = () => {
  const { t } = useTranslation("chat");

  return (
    <Card>
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
    </Card>
  );
};
