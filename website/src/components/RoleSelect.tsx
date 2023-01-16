import { Select, SelectProps } from "@chakra-ui/react";
import { forwardRef } from "react";
import { ElementOf } from "src/types/utils";

export const roles = ["general", "admin", "banned"] as const;
export type Role = ElementOf<typeof roles>;

type RoleSelectProps = Omit<SelectProps, "defaultValue"> & {
  defaultValue?: Role;
  value?: Role;
};

export const RoleSelect = forwardRef<HTMLSelectElement, RoleSelectProps>((props, ref) => {
  return (
    <Select {...props} ref={ref}>
      {roles.map((role) => (
        <option value={role} key={role}>
          {role}
        </option>
      ))}
    </Select>
  );
});

RoleSelect.displayName = "RoleSelect";
