import { Flex, Link, Tooltip } from "@chakra-ui/react";
import { SiDiscord, SiGoogle } from "@icons-pack/react-simple-icons";
import { Mail } from "lucide-react";
import NextLink from "next/link";
import { useHasAnyRole } from "src/hooks/auth/useHasAnyRole";
import { ROUTES } from "src/lib/routes";
import type { LoginProviders } from "src/types/Providers";

import { UserAvatar } from "./UserAvatar";

const AUTH_METHOD_TO_ICON: Record<LoginProviders, JSX.Element> = {
  local: <Mail size="20" />,
  discord: <SiDiscord size="20" />,
  google: <SiGoogle size="20" />,
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
          <Link as={NextLink} href={ROUTES.ADMIN_USER_DETAIL(userId)}>
            {displayName}
          </Link>
          <Tooltip label={`Signed in with ${authMethod}`}>{AUTH_METHOD_TO_ICON[authMethod]}</Tooltip>
        </>
      ) : (
        displayName
      )}
    </Flex>
  );
};
