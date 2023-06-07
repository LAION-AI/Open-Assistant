import { Flex, Link, Tooltip } from "@chakra-ui/react";
import { Discord, Google } from "@icons-pack/react-simple-icons";
import { Bot, Mail } from "lucide-react";
import NextLink from "next/link";
import { useHasAnyRole } from "src/hooks/auth/useHasAnyRole";
import { ROUTES } from "src/lib/routes";
import type { AuthMethod } from "src/types/Providers";

import { UserAvatar } from "./UserAvatar";

const AUTH_METHOD_TO_ICON: Record<AuthMethod, JSX.Element> = {
  local: <Mail size="20" />,
  discord: <Discord size="20" />,
  google: <Google size="20" />,
  system: <Bot size="20" />,
};

export const UserDisplayNameCell = ({
  displayName,
  avatarUrl,
  userId,
  authMethod,
}: {
  displayName: string;
  avatarUrl?: string;
  userId: string;
  authMethod: string;
}) => {
  const isAdminOrMod = useHasAnyRole(["admin", "moderator"]);

  return (
    <Flex gap="2" alignItems="center">
      <UserAvatar displayName={displayName} avatarUrl={avatarUrl} />
      {isAdminOrMod ? (
        <>
          <Link as={NextLink} href={ROUTES.ADMIN_USER_DETAIL(userId)} style={{ overflow: "hidden" }}>
            {displayName}
          </Link>
          {AUTH_METHOD_TO_ICON[authMethod] && (
            <Tooltip label={`Signed in with ${authMethod}`}>{AUTH_METHOD_TO_ICON[authMethod]}</Tooltip>
          )}
        </>
      ) : (
        <div style={{ overflow: "hidden" }}>{displayName}</div>
      )}
    </Flex>
  );
};
