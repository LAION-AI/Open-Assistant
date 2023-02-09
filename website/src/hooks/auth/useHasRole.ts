import { useSession } from "next-auth/react";
import { Role } from "src/components/RoleSelect";

export const useHasRole = (role: Role) => {
  const { data: session } = useSession();

  return session?.user?.role === role;
};
