import { useColorModeValue, useToken } from "@chakra-ui/react";
import { useCallback } from "react";
import { colors } from "src/styles/Theme/colors";

import { DataTableRowPropsCallback } from "../DataTable/DataTable";

export const useBoardRowProps = <T extends { highlighted: boolean }>() => {
  const borderColor = useToken("colors", useColorModeValue(colors.light.active, colors.dark.active));
  return useCallback<DataTableRowPropsCallback<T>>(
    (row) => {
      const rowData = row.original;
      return rowData.highlighted
        ? {
            sx: {
              // https://stackoverflow.com/questions/37963524/how-to-apply-border-radius-to-tr-in-bootstrap
              position: "relative",
              "td:first-of-type:before": {
                borderLeft: `6px solid ${borderColor}`,
                content: `""`,
                display: "block",
                width: "10px",
                height: "100%",
                left: 0,
                top: 0,
                borderRadius: "6px 0 0 6px",
                position: "absolute",
              },
            },
          }
        : {};
    },
    [borderColor]
  );
};
