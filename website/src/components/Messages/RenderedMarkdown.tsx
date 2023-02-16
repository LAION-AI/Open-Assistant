import { SystemStyleObject } from "@chakra-ui/react";
import { Prose } from "@nikolovlazar/chakra-ui-prose";
import { memo } from "react";
import { ReactMarkdown } from "react-markdown/lib/react-markdown";
import { Prism as SyntaxHighlighter } from "react-syntax-highlighter";
import { oneDark } from "react-syntax-highlighter/dist/cjs/styles/prism";
import remarkGfm from "remark-gfm";
interface RenderedMarkdownProps {
  markdown: string;
}

const components = {
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
};

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
    mt: { base: 1.5, md: 0 },
  },
  p: {
    whiteSpace: "pre-wrap",
    display: "inline-block",
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

// eslint-disable-next-line react/display-name
const RenderedMarkdown = memo(({ markdown }: RenderedMarkdownProps) => {
  return (
    <Prose as="div" sx={sx}>
      <ReactMarkdown remarkPlugins={plugins} components={components}>
        {markdown}
      </ReactMarkdown>
    </Prose>
  );
});

export default RenderedMarkdown;
