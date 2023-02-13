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

const sx = {
  pre: {
    bg: "transparent",
  },
  code: {
    before: {
      content: `""`, // charka prose come with "`" by default
    },
  },
};

// eslint-disable-next-line react/display-name
const RenderedMarkdown = memo(({ markdown }: RenderedMarkdownProps) => {
  return (
    <Prose sx={sx}>
      <ReactMarkdown remarkPlugins={[remarkGfm]} components={components}>
        {markdown}
      </ReactMarkdown>
    </Prose>
  );
});

export default RenderedMarkdown;
