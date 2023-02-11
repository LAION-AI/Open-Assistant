import { Select, SelectProps } from "@chakra-ui/react";
import { forwardRef } from "react";
import { ValueOf } from "ts-essentials";

export const ROLES = {
  GERNERAL: "general",
  BANNED: "banned",
  ADMIN: "admin",
  MODERATOR: "moderator",
} as const;

export type Role = ValueOf<typeof ROLES>;

type RoleSelectProps = Omit<SelectProps, "defaultValue"> & {
  defaultValue?: Role;
  value?: Role;
};

export const RoleSelect = forwardRef<HTMLSelectElement, RoleSelectProps>((props, ref) => {
  return (
    <Select {...props} ref={ref}>
      {Object.values(ROLES).map((role) => (
        <option value={role} key={role}>
          {role}
        </option>
      ))}
    </Select>
  );
});

RoleSelect.displayName = "RoleSelect";
