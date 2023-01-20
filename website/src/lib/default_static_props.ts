import { serverSideTranslations } from "next-i18next/serverSideTranslations";

export const getDefaultStaticProps = async ({ locale }) => ({
  props: {
    ...(await serverSideTranslations(locale)),
  },
});
