import { NextRouter } from "next/router";

const noop = () => undefined;

export function createMockRouter(router: Partial<NextRouter>): NextRouter {
  const mockRouter: NextRouter = {
    route: "/",
    pathname: "/",
    query: {},
    asPath: "/",
    basePath: "",
    defaultLocale: "en",
    domainLocales: [],
    isLocaleDomain: false,
    locales: ["en", "es", "fr", "ja", "pt-BR", "ru", "zh-CN", "zh-TW"],
    push: noop,
    replace: noop,
    reload: noop,
    back: noop,
    forward: noop,
    prefetch: noop,
    beforePopState: noop,
    isFallback: false,
    isReady: true,
    isPreview: false,
    events: {
      on: noop,
      off: noop,
      emit: noop,
    },
    ...router,
  };
  return mockRouter;
}
