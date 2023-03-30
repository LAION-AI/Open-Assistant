import { serverSideTranslations } from "next-i18next/serverSideTranslations";

export const getDefaultServerSideProps = async ({ locale }) => ({
  props: {
    ...(await serverSideTranslations(locale)),
  },
});

export const getStaticProps = getDefaultServerSideProps;
export const getServerSideProps = getDefaultServerSideProps;
