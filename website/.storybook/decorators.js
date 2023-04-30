import { RouterContext } from "next/dist/shared/lib/router-context";
import { SessionProvider } from "next-auth/react";
import { createMockRouter } from 'src/test-utils/createMockRouter'

export const SessionDecorator = (Story) => (
  <SessionProvider>
    <Story />
  </SessionProvider>
)
export const RouterDecorator = (Story) => {
  const router = createMockRouter()
  return (
    <RouterContext.Provider value={router}>
      <Story />
    </RouterContext.Provider>
  )
}
