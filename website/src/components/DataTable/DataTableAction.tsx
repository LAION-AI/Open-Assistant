import { forwardRef, IconButton, IconButtonProps } from "@chakra-ui/react";
import { LucideIcon } from "lucide-react";

export type DataTableActionProps = Omit<IconButtonProps, "icon" | "size"> & { icon: LucideIcon };

// need to use forwardRef from Charka to support `as` props
// https://chakra-ui.com/community/recipes/as-prop
export const DataTableAction = forwardRef<DataTableActionProps, "button">((props: DataTableActionProps, ref) => {
  return <IconButton size="sm" {...props} icon={<props.icon size="20"></props.icon>} ref={ref} />;
});
