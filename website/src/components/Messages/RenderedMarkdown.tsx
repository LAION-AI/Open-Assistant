import {
  Box,
  Button,
  Modal,
  ModalBody,
  ModalCloseButton,
  ModalContent,
  ModalFooter,
  ModalHeader,
  ModalOverlay,
  SystemStyleObject,
  useDisclosure,
} from "@chakra-ui/react";
import { Prose } from "@nikolovlazar/chakra-ui-prose";
import NextLink from "next/link";
import { useTranslation } from "next-i18next";
import { memo, MouseEvent, useMemo, useState } from "react";
import ReactMarkdown from "react-markdown";
import type { ReactMarkdownOptions } from "react-markdown/lib/react-markdown";
import { Prism as SyntaxHighlighter } from "react-syntax-highlighter";
import { oneDark } from "react-syntax-highlighter/dist/cjs/styles/prism";
import remarkGfm from "remark-gfm";
interface RenderedMarkdownProps {
  markdown: string;
}

const sx: SystemStyleObject = {
  overflowX: "auto",
  pre: {
    bg: "transparent",
  },
  code: {
    before: {
      content: `""`, // charka prose come with "`" by default
    },
    bg: "gray.300",
    p: 0.5,
    borderRadius: "2px",
    _dark: {
      bg: "gray.700",
    },
  },
  "p:only-child": {
    my: 0, // ovoid margin when markdown only render 1 p tag
  },
  p: {
    whiteSpace: "pre-wrap",
    mb: 4,
    fontSize: "md",
    fontWeight: "normal",
    lineHeight: 6,
  },
  wordBreak: "break-word",
  "> blockquote": {
    borderInlineStartColor: "gray.300",
    _dark: {
      borderInlineStartColor: "gray.500",
    },
  },
  "table tbody tr": {
    borderBottomColor: "gray.400",
    _dark: {
      borderBottomColor: "gray.700",
    },
  },
  "table thead tr": {
    borderBottomColor: "gray.400",
    borderBottomWidth: "1px",
    _dark: {
      borderBottomColor: "gray.700",
    },
  },
};

const plugins = [remarkGfm];

const disallowedElements = ["img"];

// eslint-disable-next-line react/display-name
const RenderedMarkdown = ({ markdown }: RenderedMarkdownProps) => {
  const { isOpen, onOpen, onClose } = useDisclosure();
  const [link, setLink] = useState<string | undefined>();

  const components: ReactMarkdownOptions["components"] = useMemo(() => {
    return {
      // eslint-disable-next-line @typescript-eslint/no-unused-vars
      code({ node, inline, className, children, style, ...props }) {
        const match = /language-(\w+)/.exec(className || "");
        const lang = match ? match[1] : "";
        return !inline ? (
          <SyntaxHighlighter style={oneDark} language={lang} {...props}>
            {String(children).replace(/\n$/, "")}
          </SyntaxHighlighter>
        ) : (
          <code className={className} {...props}>
            {children}
          </code>
        );
      },
      a({ href, ...props }) {
        if (!href) {
          return props.children;
        }

        return (
          <NextLink // use NextLink to handle locale if link is our internal, but it's really edge case.
            {...props}
            href={href}
            target="_blank"
            rel="noopener noreferrer"
            onClick={(e: MouseEvent) => {
              e.preventDefault();
              setLink(href);
              onOpen();
            }}
          ></NextLink>
        );
      },
    } as ReactMarkdownOptions["components"];
  }, [onOpen]);

  const linkProps = useMemo(() => {
    return {
      as: NextLink,
      href: link,
      target: "_blank",
      rel: "noopener noreferrer",
    };
  }, [link]);

  const { t } = useTranslation(["common", "message"]);

  return (
    <>
      <MemorizedMarkdown components={components}>{markdown}</MemorizedMarkdown>
      <Modal isOpen={isOpen} onClose={onClose} isCentered>
        <ModalOverlay />
        <ModalContent>
          <ModalHeader>{t("message:confirm_open_link_header")}</ModalHeader>
          <ModalCloseButton />
          <ModalBody>
            <div>{t("message:confirm_open_link_body")}</div>
            <Box textDecoration="underline" {...linkProps}>
              {link}
            </Box>
          </ModalBody>
          <ModalFooter>
            <Button variant="ghost" mr={3} onClick={onClose}>
              {t("cancel")}
            </Button>
            <Button colorScheme="blue" as={NextLink} {...linkProps} onClick={onClose}>
              {t("confirm")}
            </Button>
          </ModalFooter>
        </ModalContent>
      </Modal>
    </>
  );
};

// eslint-disable-next-line react/display-name
const MemorizedMarkdown = memo((props: ReactMarkdownOptions) => {
  return (
    <Prose as="div" sx={sx}>
      <ReactMarkdown {...props} disallowedElements={disallowedElements} remarkPlugins={plugins}></ReactMarkdown>
    </Prose>
  );
});

export default RenderedMarkdown;
