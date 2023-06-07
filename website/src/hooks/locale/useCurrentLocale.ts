import { useRouter } from "next/router";

export const useCurrentLocale = () => useRouter().locale || "en";
