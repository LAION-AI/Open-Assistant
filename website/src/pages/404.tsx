import { Box, Button, Center, Link, Text, theme, useColorModeValue } from "@chakra-ui/react";
import { useTranslation } from "next-i18next";
import { AlertTriangle } from "lucide-react";
import Head from "next/head";
import { EmptyState } from "src/components/EmptyState";
import { getTransparentHeaderLayout } from "src/components/Layout";
export { getDefaultStaticProps as getStaticProps } from "src/lib/default_static_props";

function Error() {
  const { t } = useTranslation();
  const iconColor = useColorModeValue(theme.colors.blue[500], theme.colors.blue[300]);
  return (
    <>
      <Head>
        <title>404 - Open Assistant</title>
        <meta name="404" content="Sorry, this page doesn't exist." />
      </Head>
      <Center flexDirection="column" gap="4" fontSize="lg" className="subpixel-antialiased oa-basic-theme">
        <EmptyState text={t("sorry_404")} icon={AlertTriangle} />
        <Box display="flex" flexDirection="column" alignItems="center" gap="2" mt="6">
          <Text fontSize="sm">{t("bug_description")}</Text>
          <Button
            width="fit-content"
            leftIcon={<AlertTriangle size={"1em"} color={iconColor} aria-hidden="false" />}
            variant="solid"
            size="xs"
          >
            <Link
              key="Report a Bug"
              href="https://github.com/LAION-AI/Open-Assistant/issues/new/choose"
              aria-label="Report a Bug"
              className="flex items-center"
              _hover={{ textDecoration: "none" }}
              isExternal
            >
              {t("bug_button")}
            </Link>
          </Button>
        </Box>
      </Center>
    </>
  );
}

Error.getLayout = getTransparentHeaderLayout;

export default Error;
