import "bytemd/dist/index.css";

import gfm from "@bytemd/plugin-gfm";
import math from "@bytemd/plugin-math";
import { Editor } from "@bytemd/react";
import { Box, BoxProps, Flex, Link, Text } from "@chakra-ui/react";
import { useTranslation } from "next-i18next";
import { useEffect, useMemo } from "react";

const editorConfig = {
  autofocus: true,
};

const plugins = [gfm(), math()];

const sx: BoxProps["sx"] = {
  position: "relative",
  ".bytemd": {
    h: "full",
  },
  ".CodeMirror-sizer": {
    minH: "150px !important",
  },
  ".bytemd-editor": {
    w: "100% !important",
  },
  ".bytemd-preview": {
    display: "none",
    w: 0,
  },
  ".bytemd-toolbar-tab, .bytemd-status-right, .bytemd-toolbar-right": {
    display: "none",
  },
  ".CodeMirror .CodeMirror-lines": {
    maxW: "100% !important",
  },
  ".bytemd-status-left": {
    display: { base: "none", sm: "inline" },
  },
  ".bytemd-status": {
    h: "24px",
    ps: 6,
  },
  _dark: {
    ".bytemd, .bytemd-body, .CodeMirror": {
      bg: "gray.800",
      color: "white",
      borderColor: "gray.200 !important",
    },
    ".bytemd-toolbar": {
      bg: "gray.800",
    },
    ".CodeMirror-cursors, .CodeMirror-cursor": {
      borderColor: "white !important",
    },
    ".cm-s-default .cm-variable-2": {
      color: "initial",
    },
    ".cm-s-default .cm-header": {
      color: "#6d6df1",
    },
  },
};

// until https://github.com/bytedance/bytemd/issues/265 is fixed:
const rtlSx: BoxProps["sx"] = {
  ".CodeMirror-line": {
    direction: "rtl",
  },
};

export const MarkDownEditor = (props: { value: string; onChange: (value: string) => void; placeholder?: string }) => {
  const { t, i18n } = useTranslation("tasks");
  const dir = i18n.dir();

  const boxSx = useMemo(() => {
    if (dir === "rtl") {
      return { ...sx, ...rtlSx };
    }
    return sx;
  }, [dir]);

  useEffect(() => {
    // hack to support cypress testing
    document?.querySelector(".bytemd-editor").setAttribute("data-cy", "reply");
  }, []);

  return (
    <Box sx={boxSx}>
      <Editor mode="split" editorConfig={editorConfig} plugins={plugins} {...props} data-cy="reply" />
      <Link
        href="https://www.markdownguide.org/basic-syntax"
        rel="noopener noreferrer nofollow"
        target="_blank"
        position="absolute"
        bottom="0.5"
        right={4}
        fontSize="sm"
      >
        <Flex gap="2" alignItems="center">
          <svg
            xmlns="http://www.w3.org/2000/svg"
            width="20"
            height="20"
            viewBox="0 0 24 24"
            strokeWidth="2"
            stroke="currentColor"
            fill="none"
            strokeLinecap="round"
            strokeLinejoin="round"
          >
            <path stroke="none" d="M0 0h24v24H0z" fill="none"></path>
            <path d="M3 5m0 2a2 2 0 0 1 2 -2h14a2 2 0 0 1 2 2v10a2 2 0 0 1 -2 2h-14a2 2 0 0 1 -2 -2z"></path>
            <path d="M7 15v-6l2 2l2 -2v6"></path>
            <path d="M14 13l2 2l2 -2m-2 2v-6"></path>
          </svg>
          <Text fontSize="xs">{t("default.markdownguide")}</Text>
        </Flex>
      </Link>
    </Box>
  );
};
