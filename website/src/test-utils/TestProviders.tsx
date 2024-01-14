import { RouterContext } from "next/dist/shared/lib/router-context";
import { NextRouter } from "next/router";
import { SessionProvider } from "next-auth/react";
import { PropsWithChildren } from "react";

import { createMockRouter } from "./createMockRouter";

const mockRouter = createMockRouter({});
// TODO: better session mock, should be improved with upcoming tests
const mockSession = {};
// the i18n is initialized in `jest.setup.js`, i18next does not have a clean way
// of adding a provider context
export const TestProviders = ({
  router,
  session,
  children,
}: PropsWithChildren<{ router?: NextRouter; session?: any }> = {}) => {
  return (
    <RouterContext.Provider value={router ?? mockRouter}>
      <SessionProvider session={session ?? mockSession}>{children}</SessionProvider>
    </RouterContext.Provider>
  );
};
