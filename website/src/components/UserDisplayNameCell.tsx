import { Flex, Link, Tooltip } from "@chakra-ui/react";
import { Mail } from "lucide-react";
import NextLink from "next/link";
import { useHasAnyRole } from "src/hooks/auth/useHasAnyRole";
import { ROUTES } from "src/lib/routes";

import { Discord } from "./Icons/Discord";
import { UserAvatar } from "./UserAvatar";

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
  const isEmail = authMethod === "local";

  return (
    <Flex gap="2" alignItems="center">
      {avatarUrl !== undefined && <UserAvatar displayName={displayName} avatarUrl={avatarUrl} />}
      {isAdminOrMod ? (
        <>
          <Link as={NextLink} href={ROUTES.ADMIN_USER_DETAIL(userId)}>
            {displayName}
          </Link>
          <Tooltip label={`This user signin with ${isEmail ? "email" : "discord"}`}>
            {isEmail ? <Mail size="20"></Mail> : <Discord size="20"></Discord>}
          </Tooltip>
        </>
      ) : (
        displayName
      )}
    </Flex>
  );
};
